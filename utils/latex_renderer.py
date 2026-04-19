import re
import base64
import io
import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["font.family"] = ["DejaVu Sans"]

import matplotlib.pyplot as plt


class LaTeXRenderer:
    @classmethod
    def render_latex_to_base64(cls, latex: str, fontsize: int = 16) -> str:
        try:
            fig = plt.figure(figsize=(len(latex) * 0.1 + 0.5, 0.5), dpi=100)
            ax = fig.add_subplot(111)
            ax.text(
                0.5,
                0.5,
                f"${latex}$",
                fontsize=fontsize,
                ha="center",
                va="center",
                usetex=True,
            )
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
            print(f"LaTeX render error: {e}")
            return None

    @classmethod
    def extract_latex_blocks(cls, text: str) -> list:
        blocks = []

        pattern = r"\$\$([\s\S]+?)\$\$"
        matches = re.finditer(pattern, text)
        for match in matches:
            latex = match.group(1).strip()
            if latex:
                blocks.append(
                    {
                        "type": "display",
                        "latex": latex,
                        "start": match.start(),
                        "end": match.end(),
                    }
                )

        pattern = r"(?<!\$)\$([^\$\n]+?)\$(?!\$)"
        matches = re.finditer(pattern, text)
        for match in matches:
            latex = match.group(1).strip()
            if latex and len(latex) > 1:
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
