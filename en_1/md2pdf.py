import re
import sys
from markdown_it import MarkdownIt
from markdown_it.renderer import RendererHTML
from markdown_it.token import Token

# ── Read Markdown ──────────────────────────────────────────────
SRC = "保研英语终极复习资料.md"
OUT_HTML = "保研英语终极复习资料_print.html"
OUT_PDF = "保研英语终极复习资料.pdf"

with open(SRC, "r", encoding="utf-8") as f:
    md_text = f.read()

# ── Remove original TOC section (replaced by our own with page refs) ──
# Remove the "---" before TOC, the "# 目录" heading, TOC list, and the closing "---"
md_text = re.sub(
    r'\n---\s*\n# 目录\s*\n.*?\n---\s*\n',
    '\n\n',
    md_text,
    flags=re.MULTILINE | re.DOTALL
)

# ── Convert to HTML ────────────────────────────────────────────
md = MarkdownIt("commonmark", {"html": True, "breaks": True, "typographer": True, "linkify": False})

# Enable table support (GFM tables) and strikethrough
md.options["tables"] = True
md.enable("strikethrough")

html_body = md.render(md_text)


# ── Fix heading IDs to match TOC anchor links ──────────────────
# The Markdown TOC links use pattern like: #第一部分保研英语考核全景分析
# (Chinese colon ：, spaces, and some punctuation are stripped)
# We generate IDs by: taking heading text, removing ：, spaces, and keeping Chinese+ASCII

def make_heading_id(text):
    """Generate an ID from heading text that matches the TOC link pattern."""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove Chinese colons
    text = text.replace('：', '').replace(':', '')
    # Remove parenthetical notes like （重点）（核心）（可选）etc.
    text = re.sub(r'（[^）]*）', '', text)
    text = re.sub(r'\([^)]*\)', '', text)
    # Remove spaces
    text = text.replace(' ', '').replace(' ', '')
    return text


# Post-process HTML to add IDs to headings
def add_heading_ids(html):
    """Add id attributes to h1-h6 tags based on their text content."""
    def replacer(m):
        tag = m.group(1)  # h1, h2, etc.
        content = m.group(2)
        id_val = make_heading_id(content)
        return f'<{tag} id="{id_val}">{content}</{tag}>'

    # Match heading tags without existing IDs
    html = re.sub(r'<(h[1-6])>(.*?)</\1>', replacer, html)
    return html


html_body = add_heading_ids(html_body)


# ── Assemble full HTML with Prince CSS ─────────────────────────
FULL_HTML = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>保研英语终极复习资料</title>
<style>
  /* ── Page Setup ───────────────────────────────── */
  @page {{
    size: A4;
    margin: 2.2cm 2cm 2.8cm 2cm;
    @bottom-center {{
      content: counter(page);
      font-family: "Noto Sans SC", sans-serif;
      font-size: 10pt;
      color: #555;
      vertical-align: top;
      padding-top: 10pt;
    }}
  }}

  @page :first {{
    @bottom-center {{
      content: none;
    }}
  }}

  /* ── Cover page / Title styling ──────────────── */
  body {{
    font-family: "Noto Serif SC", "SimSun", serif;
    font-size: 11pt;
    line-height: 1.85;
    color: #222;
  }}

  /* ── Table of Contents (auto page refs) ──────── */
  .toc-wrapper {{
    page-break-after: always;
  }}

  .toc-wrapper h1 {{
    font-family: "Noto Sans SC", sans-serif;
    font-size: 20pt;
    text-align: center;
    margin-bottom: 24pt;
    padding-bottom: 10pt;
    border-bottom: 2px solid #333;
  }}

  .toc-wrapper ul {{
    list-style: none;
    padding: 0;
    margin: 0;
  }}

  .toc-wrapper li {{
    margin: 6pt 0;
    font-size: 11.5pt;
    line-height: 1.6;
  }}

  .toc-wrapper li a {{
    text-decoration: none;
    color: #222;
    display: flex;
    justify-content: space-between;
  }}

  .toc-wrapper li a::after {{
    content: target-counter(attr(href), page);
    font-variant-numeric: tabular-nums;
    color: #555;
  }}

  /* Leader dots for TOC entries */
  .toc-wrapper li.toc-h2 {{
    padding-left: 18pt;
  }}

  /* ── Headings ────────────────────────────────── */
  h1 {{
    font-family: "Noto Sans SC", sans-serif;
    font-size: 18pt;
    font-weight: 700;
    color: #1a1a1a;
    margin-top: 28pt;
    margin-bottom: 14pt;
    padding-bottom: 6pt;
    border-bottom: 1.5px solid #888;
    page-break-before: always;
  }}

  h1:first-of-type {{
    page-break-before: avoid;
  }}

  h2 {{
    font-family: "Noto Sans SC", sans-serif;
    font-size: 14pt;
    font-weight: 600;
    color: #2a2a2a;
    margin-top: 22pt;
    margin-bottom: 10pt;
  }}

  h3 {{
    font-family: "Noto Sans SC", sans-serif;
    font-size: 12pt;
    font-weight: 600;
    color: #333;
    margin-top: 16pt;
    margin-bottom: 8pt;
  }}

  /* ── Tables ──────────────────────────────────── */
  table {{
    border-collapse: collapse;
    width: 100%;
    margin: 10pt 0 16pt 0;
    font-size: 9.5pt;
    page-break-inside: avoid;
  }}

  th {{
    background-color: #3a3a3a;
    color: white;
    padding: 6pt 8pt;
    text-align: left;
    font-family: "Noto Sans SC", sans-serif;
    font-weight: 600;
  }}

  td {{
    padding: 5pt 8pt;
    border-bottom: 0.5px solid #ccc;
    vertical-align: top;
  }}

  tr:nth-child(even) td {{
    background-color: #f7f7f7;
  }}

  /* ── Code ────────────────────────────────────── */
  code {{
    font-family: "Consolas", "Courier New", monospace;
    font-size: 9pt;
    background-color: #f0f0f0;
    padding: 1pt 4pt;
    border-radius: 2pt;
    word-break: break-all;
  }}

  pre {{
    background-color: #f5f5f5;
    border-left: 3px solid #666;
    padding: 10pt 12pt;
    font-size: 9pt;
    line-height: 1.5;
    overflow-x: auto;
    white-space: pre-wrap;
    word-wrap: break-word;
    page-break-inside: avoid;
  }}

  pre code {{
    background: none;
    padding: 0;
    font-size: 9pt;
  }}

  /* ── Blockquotes ─────────────────────────────── */
  blockquote {{
    border-left: 3px solid #bbb;
    margin: 10pt 0;
    padding: 6pt 14pt;
    color: #555;
    background: #fafafa;
    font-size: 10.5pt;
  }}

  blockquote p {{
    margin: 4pt 0;
  }}

  /* ── Lists ───────────────────────────────────── */
  ul, ol {{
    margin: 6pt 0 10pt 0;
    padding-left: 24pt;
  }}

  li {{
    margin: 3pt 0;
  }}

  /* ── Paragraphs ──────────────────────────────── */
  p {{
    margin: 6pt 0;
  }}

  /* ── Horizontal Rules ────────────────────────── */
  hr {{
    border: none;
    border-top: 1px solid #ccc;
    margin: 20pt 0;
  }}

  /* ── Strong / Emphasis ───────────────────────── */
  strong {{
    color: #1a1a1a;
  }}

  /* ── Links ───────────────────────────────────── */
  a {{
    color: #2a5db0;
  }}

  /* ── Inline images / math (keep printable) ───── */
  img {{
    max-width: 100%;
  }}

  /* ── Checkmark / Arrow lists in markdown ─────── */
  /* Prevent page breaks inside small blocks */
  li, p, td {{
    page-break-inside: avoid;
  }}
</style>
</head>
<body>

<!-- ═══════════ TABLE OF CONTENTS ═══════════ -->
<div class="toc-wrapper">
<h1>目 录</h1>
<ul>
  <li><a href="#第一部分保研英语考核全景分析">第一部分：保研英语考核全景分析</a></li>
  <li><a href="#第二部分专业英语核心词汇库">第二部分：专业英语核心词汇库</a></li>
  <li><a href="#第三部分英文自我介绍终极模板">第三部分：英文自我介绍终极模板</a></li>
  <li><a href="#第四部分英文项目介绍训练">第四部分：英文项目介绍训练</a></li>
  <li><a href="#第五部分专业英语问答题库">第五部分：专业英语问答题库（重点）</a></li>
  <li><a href="#第六部分文献翻译专项训练">第六部分：文献翻译专项训练（核心）</a></li>
  <li><a href="#第七部分论文摘要阅读训练">第七部分：论文摘要阅读训练</a></li>
  <li><a href="#第八部分科研英语表达训练">第八部分：科研英语表达训练</a></li>
  <li><a href="#第九部分高频翻译术语库">第九部分：高频翻译术语库</a></li>
  <li><a href="#第十部分保研英语模拟面试">第十部分：保研英语模拟面试</a></li>
  <li><a href="#第十一部分最终冲刺复习方案">第十一部分：最终冲刺复习方案</a></li>
</ul>
</div>

<!-- ═══════════ MAIN CONTENT ═══════════ -->
{html_body}

</body>
</html>'''

# ── Write HTML ──────────────────────────────────────────────────
with open(OUT_HTML, "w", encoding="utf-8") as f:
    f.write(FULL_HTML)

print(f"HTML written to: {OUT_HTML}")
print(f"Ready for Prince PDF generation.")
