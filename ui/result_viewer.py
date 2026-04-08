from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtGui import QTextCursor
from PyQt5.QtCore import Qt


class ResultViewer(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
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

    def set_markdown(self, text: str):
        self._render_markdown(text)

    def _render_markdown(self, text: str):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Start)

        formatted = self._format_markdown(text)
        cursor.insertHtml(formatted)

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
                num, content = re.match(r"^(\d+)\.\s(.*)", line).groups()
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
