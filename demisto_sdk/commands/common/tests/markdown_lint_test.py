import socket

import pytest

from demisto_sdk.commands.common.hook_validations.readme import ReadMeValidator
from demisto_sdk.commands.common.markdown_lint import run_markdownlint


def _mdx_server_reachable() -> bool:
    try:
        with socket.create_connection(("127.0.0.1", 6161), timeout=0.5):
            return True
    except OSError:
        return False


# `ReadMeValidator.start_mdx_server()` tries Docker first, then a local Node
# server with markdown-lint installed; if neither is available it silently
# returns an empty context manager that yields False, and these tests then
# fail trying to hit 127.0.0.1:6161. Skip honestly when the server isn't up.
requires_mdx_server = pytest.mark.skipif(
    not _mdx_server_reachable(),
    reason="requires MDX server (Docker or local Node) on 127.0.0.1:6161",
)


@pytest.mark.parametrize(
    "file_content, expected_error",
    [
        ("##Hello", "no-missing-space-atx"),
        (
            """
## Unreleased

   * Feature1
* feature2""",
            "list-indent",
        ),
        (
            """## Header
    next line""",
            "blanks-around-headings",
        ),
        ("<p>something</p>", "no-inline-html"),
    ],
)
@requires_mdx_server
def test_markdown_validations(file_content, expected_error):
    """
    Given: Markdown text with an issue
    When: calling run_markdownlint
    Then: Receive a response whose fixed text is equal to expected result
    """
    with ReadMeValidator.start_mdx_server():
        response = run_markdownlint(file_content)
        assert response.has_errors
        assert expected_error in response.validations


@pytest.mark.parametrize(
    "file_content, expected_fix",
    [
        ("##Hello", "## Hello"),
        (
            """## Unreleased

   * Feature1
- feature2""",
            """## Unreleased

* Feature1
* feature2""",
        ),
        (
            """## Header
    next line""",
            """## Header

    next line""",
        ),
    ],
)
@requires_mdx_server
def test_markdown_fixes(file_content, expected_fix):
    """
    Given: Markdown text with a fixable issue
    When: calling run_markdownlint
    Then: Recieve a response whose fixed text is equal to expected result
    """
    with ReadMeValidator.start_mdx_server():
        response = run_markdownlint(file_content, fix=True)
        assert not response.has_errors, response
        assert not response.validations, response.validations
        assert expected_fix == response.fixed_text, response.fixed_text


@requires_mdx_server
def test_disabled_rule():
    # Tests no h1 header and duplicate headers rule not active. Just to ensure config working properly
    with ReadMeValidator.start_mdx_server():
        assert not run_markdownlint(
            "## Hello\n\n## Hello"
        ).has_errors, run_markdownlint("## Hello\n\n## Hello").validations


@requires_mdx_server
def test_filename_returned_in_validations():
    # Tests no h1 header and duplicate headers rule not active. Just to ensure config working properly
    with ReadMeValidator.start_mdx_server():
        filename = "helloworld124"
        assert filename in run_markdownlint("##Hello", file_path=filename).validations
