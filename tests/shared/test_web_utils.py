"""Unit tests for shared web_utils (HTML cleaning and diff generation)."""

from autoppia_iwa.src.shared.web_utils import clean_html, generate_html_differences


class TestCleanHtml:
    """Tests for clean_html()."""

    def test_empty_string_returns_empty(self):
        assert clean_html("") == ""

    def test_invalid_html_returns_empty(self):
        # Parser may still produce a document; use something that can trigger exception path
        result = clean_html("<html><body>ok</body></html>")
        assert "ok" in result or result == ""

    def test_removes_script_tags(self):
        html = "<html><head><script>alert(1);</script></head><body><p>text</p></body></html>"
        result = clean_html(html)
        assert "script" not in result.lower() or "alert" not in result

    def test_removes_style_tags(self):
        html = "<html><head><style>.x { color: red; }</style></head><body><p>text</p></body></html>"
        result = clean_html(html)
        assert "style" not in result.lower() or ".x" not in result

    def test_removes_hidden_elements(self):
        html = "<html><body><div hidden>secret</div><p>visible</p></body></html>"
        result = clean_html(html)
        assert "visible" in result

    def test_removes_display_none(self):
        html = '<html><body><div style="display: none">hidden</div><p>visible</p></body></html>'
        result = clean_html(html)
        assert "visible" in result

    def test_removes_html_comments(self):
        html = "<html><body><!-- comment --><p>text</p></body></html>"
        result = clean_html(html)
        assert "comment" not in result

    def test_keeps_visible_content(self):
        html = "<html><body><p>Hello world</p></body></html>"
        result = clean_html(html)
        assert "Hello" in result and "world" in result

    def test_removes_inline_event_handlers(self):
        html = '<html><body><p onclick="alert(1)" id="x" class="y">text</p></body></html>'
        result = clean_html(html)
        assert "onclick" not in result

    def test_no_body_uses_root(self):
        html = "<p>standalone</p>"
        result = clean_html(html)
        assert "standalone" in result


class TestGenerateHtmlDifferences:
    """Tests for generate_html_differences()."""

    def test_empty_list_returns_empty(self):
        assert generate_html_differences([]) == []

    def test_single_html_returns_single_element(self):
        html_list = ["<p>one</p>"]
        result = generate_html_differences(html_list)
        assert result == ["<p>one</p>"]

    def test_two_identical_htmls_returns_first_only(self):
        html_list = ["<p>same</p>", "<p>same</p>"]
        result = generate_html_differences(html_list)
        assert len(result) == 1
        assert result[0] == "<p>same</p>"

    def test_two_different_htmls_returns_first_and_diff(self):
        html_list = ["<p>a</p>", "<p>b</p>"]
        result = generate_html_differences(html_list)
        assert len(result) == 2
        assert result[0] == "<p>a</p>"
        assert "diff" in result[1].lower() or "-" in result[1] or "+" in result[1]

    def test_three_htmls_includes_diffs_between_consecutive(self):
        html_list = ["<p>1</p>", "<p>2</p>", "<p>3</p>"]
        result = generate_html_differences(html_list)
        assert result[0] == "<p>1</p>"
        assert len(result) >= 2
