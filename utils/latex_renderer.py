import re
import base64
import io
import warnings
import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["font.family"] = ["DejaVu Sans"]

import matplotlib.pyplot as plt


class LaTeXRenderer:
    _latex_available = None
    _checked = False

    @classmethod
    def _check_latex_available(cls) -> bool:
        if cls._checked:
            return cls._latex_available or False
        cls._checked = True

        try:
            testfig = plt.figure(figsize=(0.5, 0.5), dpi=50)
            ax = testfig.add_subplot(111)
            ax.text(0.5, 0.5, "$x$", fontsize=8, ha="center", va="center", usetex=True)
            plt.tight_layout()
            plt.savefig(io.BytesIO(), format="png", dpi=50)
            plt.close(testfig)
            cls._latex_available = True
            return True
        except Exception:
            cls._latex_available = False
            return False

    @classmethod
    def render_latex_to_base64(cls, latex: str, fontsize: int = 16) -> str:
        latex = latex.strip()
        if not latex:
            return None

        try:
            fig = plt.figure(figsize=(len(latex) * 0.08 + 0.5, 0.5), dpi=100)
            ax = fig.add_subplot(111)

            use_latex = (
                cls._check_latex_available()
                if cls._latex_available is None
                else cls._latex_available
            )

            ax.text(0.5, 0.5, f"${latex}$", fontsize=fontsize, ha="center", va="center")

            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis("off")
            plt.tight_layout(pad=0.5)

            buf = io.BytesIO()
            plt.savefig(
                buf,
                format="png",
                dpi=100,
                bbox_inches="tight",
                pad_inches=0.1,
                transparent=True,
            )
            plt.close(fig)

            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode("utf-8")
            return f"data:image/png;base64,{img_base64}"
        except Exception as e:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                try:
                    plt.close(fig)
                except Exception:
                    pass
            return None

    @classmethod
    def extract_latex_blocks(cls, text: str) -> list:
        if not text:
            return []

        blocks = []

        pattern = r"\$\$([\s\S]+?)\$\$"
        matches = re.finditer(pattern, text)
        for match in matches:
            latex = match.group(1).strip()
            if latex and len(latex) > 1:
                blocks.append(
                    {
                        "type": "display",
                        "latex": latex,
                        "start": match.start(),
                        "end": match.end(),
                    }
                )

        pattern = r"(?<!\$)\$([a-zA-Z0-9_\\{}\[\]()+=-]+)\$(?!\$)"
        matches = re.finditer(pattern, text)
        for match in matches:
            latex = match.group(1).strip()
            if latex and len(latex) > 1 and not latex.isdigit():
                blocks.append(
                    {
                        "type": "inline",
                        "latex": latex,
                        "start": match.start(),
                        "end": match.end(),
                    }
                )

        return sorted(blocks, key=lambda x: x["start"])

    @classmethod
    def replace_with_images(cls, text: str) -> str:
        blocks = cls.extract_latex_blocks(text)

        if not blocks:
            return text

        result_parts = []
        last_end = 0

        for block in blocks:
            result_parts.append(text[last_end : block["start"]])

            img_data = cls.render_latex_to_base64(
                block["latex"], fontsize=14 if block["type"] == "inline" else 18
            )

            if img_data:
                if block["type"] == "display":
                    result_parts.append(
                        f'<br/><img src="{img_data}" style="display:block;margin:15px auto;"/><br/>'
                    )
                else:
                    result_parts.append(
                        f'<img src="{img_data}" style="vertical-align:middle;"/>'
                    )
            else:
                result_parts.append(f"${block['latex']}$")

            last_end = block["end"]

        result_parts.append(text[last_end:])
        return "".join(result_parts)
