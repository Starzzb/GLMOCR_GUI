from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtGui import QTextCursor


class ResultViewer(QTextEdit):
    MODE_PLAIN = "plain"
    MODE_MARKDOWN = "markdown"
    MODE_RAW = "raw"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_mode = self.MODE_MARKDOWN
        self._raw_text = ""
        self.setReadOnly(True)
        self.setFontFamily("Consolas, Monospace")
        self.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                background: #fafafa;
            }
        """)

    def set_result(self, text: str, mode: str = None):
        self._raw_text = text
        if mode:
            self._current_mode = mode
        self._render()

    def set_mode(self, mode: str):
        if mode != self._current_mode:
            self._current_mode = mode
            self._render()

    def get_current_text(self) -> str:
        if self._current_mode == self.MODE_PLAIN:
            return self._extract_plain_text(self._raw_text)
        elif self._current_mode == self.MODE_MARKDOWN:
            return self._raw_text
        else:
            return self._raw_text

    def _render(self):
        if self._current_mode == self.MODE_PLAIN:
            self._render_plain()
        elif self._current_mode == self.MODE_MARKDOWN:
            self._render_markdown()
        else:
            self._render_raw()

    def _render_plain(self):
        plain_text = self._extract_plain_text(self._raw_text)
        self.setPlainText(plain_text)

    def _render_raw(self):
        self.setPlainText(self._raw_text)

    def _render_markdown(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Start)
        formatted = self._format_markdown(self._raw_text)
        cursor.insertHtml(formatted)

    def _extract_plain_text(self, text: str) -> str:
        import re

        text = re.sub(r"```[\s\S]*?```", "", text)
        text = re.sub(r"`[^`]+`", "", text)
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
        text = re.sub(r"\*([^*]+)\*", r"\1", text)
        text = re.sub(r"#{1,6}\s+", "", text)
        text = re.sub(r"[-*]\s+", "", text)
        text = re.sub(r"\d+\.\s+", "", text)
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        lines = text.split("\n")
        result = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith("|"):
                result.append(line)
        return "\n".join(result)

    def _format_markdown(self, text: str) -> str:
        import re

        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        lines = text.split("\n")
        html_lines = []

        in_code_block = False
        code_content = []

        for line in lines:
            if line.startswith("```"):
                if not in_code_block:
                    in_code_block = True
                    code_content = [line[3:]]
                else:
                    html_lines.append(
                        f'<pre style="background:#f4f4f4;padding:10px;border-radius:4px;"><code>{"<br>".join(code_content)}</code></pre>'
                    )
                    in_code_block = False
                    code_content = []
                continue

            if in_code_block:
                code_content.append(line)
                continue

            if line.startswith("# "):
                html_lines.append(
                    f'<h1 style="color:#333;border-bottom:1px solid #eee;padding-bottom:5px;">{line[2:]}</h1>'
                )
            elif line.startswith("## "):
                html_lines.append(f'<h2 style="color:#555;">{line[3:]}</h2>')
            elif line.startswith("### "):
                html_lines.append(f'<h3 style="color:#666;">{line[4:]}</h3>')
            elif line.startswith("- ") or line.startswith("* "):
                html_lines.append(f'<li style="margin-left:20px;">{line[2:]}</li>')
            elif re.match(r"^\d+\.\s", line):
                match = re.match(r"^(\d+)\.\s(.*)", line)
                if match:
                    num, content = match.groups()
                    html_lines.append(f'<li style="margin-left:20px;">{content}</li>')
            elif line.strip() == "":
                html_lines.append("<br>")
            else:
                line = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", line)
                line = re.sub(r"\*(.*?)\*", r"<i>\1</i>", line)
                line = re.sub(
                    r"`(.*?)`",
                    r'<code style="background:#f4f4f4;padding:2px 4px;border-radius:3px;">\1</code>',
                    line,
                )
                html_lines.append(f'<p style="margin:5px 0;">{line}</p>')

        return "".join(html_lines)
