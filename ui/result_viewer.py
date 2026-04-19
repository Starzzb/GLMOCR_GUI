from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtGui import QTextCursor, QImage, QPixmap
import markdown
from utils.latex_renderer import LaTeXRenderer


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
        self.clear()
        self.setPlainText(plain_text)

    def _render_raw(self):
        self.clear()
        self.setPlainText(self._raw_text)

    def _render_markdown(self):
        self.clear()

        text_with_latex = LaTeXRenderer.replace_with_images(self._raw_text)

        html = markdown.markdown(
            text_with_latex, extensions=["extra", "codehilite", "tables", "fenced_code"]
        )
        styled_html = self._wrap_with_styles(html)
        self.setHtml(styled_html)

    def _wrap_with_styles(self, html_content: str) -> str:
        return f"""
        <html>
        <head>
        <style>
            body {{
                font-family: Consolas, 'Courier New', monospace;
                font-size: 14px;
                line-height: 1.6;
                color: #333;
            }}
            h1, h2, h3, h4, h5, h6 {{
                color: #222;
                margin-top: 20px;
                margin-bottom: 10px;
            }}
            h1 {{ border-bottom: 2px solid #ddd; padding-bottom: 8px; }}
            h2 {{ border-bottom: 1px solid #eee; padding-bottom: 5px; }}
            p {{ margin: 10px 0; }}
            code {{
                background: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: Consolas, 'Courier New', monospace;
            }}
            pre {{
                background: #f4f4f4;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
                border: 1px solid #ddd;
            }}
            pre code {{
                background: none;
                padding: 0;
            }}
            blockquote {{
                border-left: 4px solid #ddd;
                margin: 10px 0;
                padding-left: 15px;
                color: #666;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 10px 0;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background: #f4f4f4;
            }}
            ul, ol {{
                margin: 10px 0;
                padding-left: 25px;
            }}
            li {{
                margin: 5px 0;
            }}
            img {{
                max-width: 100%;
                height: auto;
            }}
            hr {{
                border: none;
                border-top: 1px solid #ddd;
                margin: 20px 0;
            }}
        </style>
        </head>
        <body>
        {html_content}
        </body>
        </html>
        """

    def _extract_plain_text(self, text: str) -> str:
        text_with_latex = LaTeXRenderer.replace_with_images(text)
        html = markdown.markdown(text_with_latex, extensions=["fenced_code"])
        import re

        html = re.sub(r"<pre[^>]*>.*?</pre>", "", html, flags=re.DOTALL)
        html = re.sub(r"<code[^>]*>.*?</code>", "", html, flags=re.DOTALL)
        html = re.sub(r"<img[^>]*>", "", html)
        html = re.sub(r"<[^>]+>", "", html)
        html = re.sub(r"&nbsp;", " ", html)
        html = re.sub(r"&amp;", "&", html)
        html = re.sub(r"&lt;", "<", html)
        html = re.sub(r"&gt;", ">", html)
        lines = html.split("\n")
        result = []
        for line in lines:
            line = line.strip()
            if line:
                result.append(line)
        return "\n".join(result)
