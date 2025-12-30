import subprocess
import tempfile
import pathlib
import re
import sys

def inline_tailwind(input_html, output_html):
    script_dir = pathlib.Path(__file__).parent.resolve()
    tailwind_exe = script_dir / "tailwind.exe"

    if not tailwind_exe.exists():
        raise FileNotFoundError("tailwind.exe not found next to tailwind.py")

    input_html = pathlib.Path(input_html)
    output_html = pathlib.Path(output_html)

    html = input_html.read_text(encoding="utf-8")

    # Remove Tailwind CDN
    html = re.sub(
        r'<script[^>]*src=["\']https://cdn\.tailwindcss\.com["\'][^>]*></script>',
        '',
        html,
        flags=re.IGNORECASE
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = pathlib.Path(tmpdir)

        content_file = tmpdir / "content.html"
        input_css = tmpdir / "input.css"
        output_css = tmpdir / "output.css"

        content_file.write_text(html, encoding="utf-8")

        input_css.write_text(
            "@tailwind base;\n@tailwind components;\n@tailwind utilities;\n",
            encoding="utf-8"
        )

        subprocess.run(
            [
                str(tailwind_exe),
                "-i", str(input_css),
                "-o", str(output_css),
                "--content", str(content_file),
                "--minify"
            ],
            check=True
        )

        compiled_css = output_css.read_text(encoding="utf-8")

    style_tag = f"<style>\n{compiled_css}\n</style>\n"

    if "</head>" in html:
        html = html.replace("</head>", style_tag + "</head>")
    else:
        html = style_tag + html

    output_html.write_text(html, encoding="utf-8")

    print(f"✔ Tailwind inlined → {output_html}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python tailwind.py input.html output.html")
        sys.exit(1)

    inline_tailwind(sys.argv[1], sys.argv[2])
