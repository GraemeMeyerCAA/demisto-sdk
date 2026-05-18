"""Bucket failures across all JUnit XML files in windows_test_xml/ by error signature."""
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

XML_DIR = Path(r"C:\Users\robert\Code\demisto-sdk\windows_test_xml")


def normalize(text: str) -> str:
    """Strip volatile bits (paths, line numbers, addresses) so similar errors cluster."""
    # absolute Windows paths -> <p>
    text = re.sub(r"[A-Z]:\\\\?[^\s'\"<>:|?*]+", "<path>", text)
    text = re.sub(r"[A-Z]:/[^\s'\"<>:|?*]+", "<path>", text)
    # POSIX paths -> <p>
    text = re.sub(r"/(?:[\w.\-]+/)+[\w.\-]+", "<path>", text)
    # hex addresses, line numbers like ":123"
    text = re.sub(r"0x[0-9a-fA-F]+", "0xADDR", text)
    text = re.sub(r"\bat 0x[0-9a-fA-F]+\b", "at 0xADDR", text)
    text = re.sub(r":\d+(?=:)", ":<LN>", text)
    # collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def first_signature(message: str) -> str:
    """First exception-ish line of the message."""
    for line in message.splitlines():
        line = line.strip()
        if not line:
            continue
        # Skip "self = ..." pytest fixture noise
        if line.startswith("self =") or line.startswith("def "):
            continue
        return normalize(line)
    return "<empty>"


def main() -> int:
    buckets: dict[str, list[tuple[str, str]]] = defaultdict(list)  # sig -> [(file, testname)]
    totals: Counter = Counter()
    chunks: list[tuple[str, int, int, int, int]] = []  # (chunk, tests, failures, errors, skipped)

    for xml_path in sorted(XML_DIR.glob("*.xml")):
        try:
            root = ET.parse(xml_path).getroot()
        except ET.ParseError as e:
            print(f"WARN: cannot parse {xml_path.name}: {e}")
            continue
        # JUnit XML root could be <testsuite> or <testsuites>
        suites = root.findall(".//testsuite") if root.tag == "testsuites" else [root]
        chunk_tests = chunk_fail = chunk_err = chunk_skip = 0
        for suite in suites:
            chunk_tests += int(suite.attrib.get("tests", 0))
            chunk_fail += int(suite.attrib.get("failures", 0))
            chunk_err += int(suite.attrib.get("errors", 0))
            chunk_skip += int(suite.attrib.get("skipped", 0))
            for case in suite.iter("testcase"):
                name = f"{case.attrib.get('classname','?')}::{case.attrib.get('name','?')}"
                for tag in ("failure", "error"):
                    el = case.find(tag)
                    if el is not None:
                        msg = (el.attrib.get("message") or "") + "\n" + (el.text or "")
                        sig = first_signature(msg)
                        buckets[sig].append((xml_path.stem, name))
                        totals[tag] += 1
                        break
        chunks.append((xml_path.stem, chunk_tests, chunk_fail, chunk_err, chunk_skip))

    print("=" * 78)
    print("PER-CHUNK SUMMARY")
    print("=" * 78)
    print(f"{'chunk':<28} {'tests':>6} {'fail':>6} {'err':>6} {'skip':>6}")
    g_tests = g_fail = g_err = g_skip = 0
    for n, t, f, e, s in chunks:
        print(f"{n:<28} {t:>6} {f:>6} {e:>6} {s:>6}")
        g_tests += t; g_fail += f; g_err += e; g_skip += s
    print(f"{'TOTAL':<28} {g_tests:>6} {g_fail:>6} {g_err:>6} {g_skip:>6}")

    print()
    print("=" * 78)
    print("FAILURE BUCKETS (signature -> count)")
    print("=" * 78)
    sorted_buckets = sorted(buckets.items(), key=lambda kv: -len(kv[1]))
    for sig, hits in sorted_buckets[:40]:
        print(f"\n[{len(hits):>4}]  {sig[:200]}")
        # show 2 example tests
        for chunk, tn in hits[:2]:
            print(f"        e.g. {chunk}: {tn[:140]}")

    # Long tail
    rare = sum(1 for _, h in sorted_buckets if len(h) == 1)
    print()
    print(f"singleton buckets: {rare} (likely test-specific)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
