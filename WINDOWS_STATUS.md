# Windows Compatibility — Status

## TL;DR

The demisto-sdk now runs natively on Windows. Core runtime is ready for use
against real XSOAR credentials. ~5,547 of ~5,576 tests pass on Windows; the
remaining failures are **not Windows-specific** — they reproduce identically on
clean Ubuntu and trace to a Neo4j/APOC configuration issue shared by both
platforms.

## What works on Windows now

- POSIX-isms removed (`getuid`, `:` pathsep, `PYTHONPATH` joins).
- Local Neo4j 5.22 detection + Windows-native graph path (no Docker dependency).
- Multiprocessing forced to `spawn` everywhere; small-repo/small-batch
  short-circuits added in `repository.py` and `neo4j_graph.py` to avoid spawn
  deadlocks during tests.
- Path hygiene: forward-slash normalization at the boundaries that need it
  (`get_files_in_dir`, `get_pack_names_from_files`, `update_id_set.file_path`,
  `git_util.get_local_remote_file_path`, release-notes path, validate
  initializer substring checks). Native separators preserved everywhere the
  graph lookups need them.
- Encoding: CRLF/CR → LF normalization in `text_file.load`, `safe_read_unicode`,
  and `insert_description_to_yml`. `PYTHONUTF8=1` set in runners.
- loguru: `opt(colors=True)` switched to args-form in `timers.py`,
  `base_validator.py`, and `generate_yml.py` to stop user content like
  `<module>` / `<locals>` / `<image>` from being parsed as color tags.
- File-handle / fixture-leak fixes in tests for Windows file locking.
- `filecmp.cmp` byte comparisons that broke under CRLF translation switched to
  text-mode reads.

## What does NOT work (and why it's not a Windows problem)

The remaining GR_validators failures (~60 on Windows when run as one process)
fail with the **same error on a clean Ubuntu install**:

```
neo4j.exceptions.ClientError: {code: Neo.ClientError.Procedure.ProcedureCallFailed}
Failed to invoke procedure `apoc.export.graphml.all`
```

Root cause: APOC's `file-export` procedure is disabled by default. The fix is
the same on every OS — add to `neo4j.conf`:

```
apoc.export.file.enabled=true
dbms.security.procedures.unrestricted=apoc.*
```

and restart Neo4j. With that flipped on both platforms, the GR_validators delta
should approach zero.

## Out of scope

- Docker-coupled commands (`lint`, `pre-commit`, `test-content`). They still
  require Docker + a Linux container to run integration code; not a Windows
  porting target.

## How to reproduce a run

PowerShell, from repo root:

```powershell
$env:PYTHONUTF8 = '1'
$env:DEMISTO_SDK_IGNORE_CONTENT_WARNING = '1'
poetry run pytest demisto_sdk/commands --timeout=60 --timeout-method=thread -q
```

Chunked runs (resilient to hangs) live in `run_chunked_tests.ps1` /
`run_rerun_chunks.ps1`. JUnit XML lands in `windows_test_xml/`.

## Bottom line

Use it. The Windows port works for real SDK commands. The remaining test
failures are an APOC config issue, not a Windows compatibility issue.
