import markdown
import os
import re
from bs4 import BeautifulSoup

class_map = {
    "c1": "token comment",
    "o":  "token operator",
    "mf": "token number",
    "mi":  "token number",
    "p":  "token punctuation",
    "kc": "token boolean",
    "kn": "token keyword"
}

# Rules :
#   1. For latex use \subseteq and \infty instead of \sube and \infin
#   2. Only single line latex is supported i.e. enclosed in $<latex_code>$

def convert_md_to_html(md_path: str,
                       html_path: str,
                       title: str = None,
                       css_href = "https://ayman-tech.github.io/styles.css") -> None:
    """
    Convert a Markdown file to a standalone HTML file.
    Ensures every <h1>–<h6> tag in the output has class="atx".
    Args:
        md_path:   Path to the source .md file.
        html_path: Path where the output .html will be saved.
        title:     Optional HTML <title>. Defaults to the .md filename.
        css_href:  Optional href for a <link> stylesheet to inject.
    """
    # 1. Read Markdown content and add spaces
    with open(md_path, 'r', encoding='utf-8') as md_file:
        lines = md_file.readlines()

    # Add two spaces to end of each non-empty line that doesn't already have them
    processed_lines = []
    for line in lines:
        stripped = line.rstrip('\n')
        if stripped and not stripped.endswith('  ') and '<br>' not in stripped:
            stripped += '  '
        processed_lines.append(stripped + '\n')

    md_text = ''.join(processed_lines)

    # 2. Convert to HTML fragment
    html_fragment = markdown.markdown(
        md_text,
        extensions=[
            'fenced_code',
            'codehilite',
            'tables',
            'toc'
        ]
    )

    # 3. Post-process headings: add class="atx" to all <h1>–<h6>
    soup = BeautifulSoup(html_fragment, 'html.parser')
    for level in range(1, 7):
        for heading in soup.find_all(f'h{level}'):
            if level==1 and title==None:
                title = heading.string.strip()
            existing = heading.get('class', [])
            heading['class'] = existing + ['atx']

    # 4. Move stray <p> that follow a <ul> into that list’s last <li>
    for ul in soup.find_all('ul'):
        # skip whitespace/text nodes
        next_el = ul.find_next_sibling()
        while next_el and getattr(next_el, 'name', None) is None:
            next_el = next_el.find_next_sibling()

        if next_el and next_el.name == 'p':
            last_li = ul.find_all('li')[-1]
            last_li.append(next_el.extract())
    
    # 5 Change class names
    for tag in soup.find_all(class_=True):
        new_classes = []
        for cls in tag.get("class", []):
            # Replace if in map, else keep original
            replacement = class_map.get(cls, cls)
            new_classes.extend(replacement.split())  # handle multi-word classes
        tag["class"] = new_classes

    # 6. Render LaTex
    wrapper ='<span class="mathjax">{}</span>'
    pattern = re.compile(r"\$\$(.+?)\$\$", re.DOTALL)
    def replacer(match):
        latex_code = match.group(1).strip()
        return wrapper.format(latex_code)

    processed_body = pattern.sub(replacer, str(soup))

    # 7. Determine page title
    page_title = title or os.path.splitext(os.path.basename(md_path))[0]

    # 8. Build complete HTML document
    link_tag = f'<link rel="stylesheet" href="{css_href}">\n' if css_href else ''
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{page_title}</title>
  {link_tag}
  <!-- MathJax configuration and script -->
  <script>
    MathJax = {{
      tex: {{
        inlineMath: [['$', '$'], ['\\(', '\\)']],
        displayMath: [['$$', '$$'], ['\\[', '\\]']],
        processEscapes: true,
        tags: 'ams'
      }},
      svg: {{
        fontCache: 'global'
      }}
    }};
  </script>
  <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
</head>
<body>
<article class="markdown-body">
{processed_body}
</article>
</body>
</html>
"""

    # 6. Write out the HTML file
    with open(html_path, 'w', encoding='utf-8') as html_file:
        html_file.write(full_html)

if __name__ == "__main__":
    print("Enter only filenames (press enter after each) to convert without extension.")
    print("Type 'done' to finish. (default:All)")
    items = []
    while True:
        line = input("> ").strip().lower()
        if line == "done" or line=="":
            break
        if line:
            items.append(line+".md")
    check = False
    if len(items)>0:
        check=True

    for dirpath, _, filenames in os.walk("C:\\Users\\Aym_s\\projects\\github\\profile"):
        for filename in filenames:
            if filename.lower().endswith('.md'):
                if filename.lower()=="readme.md":
                    continue
                if check and filename.lower() not in items:
                    continue
                md_file = os.path.join(dirpath, filename)
                print("Converting : " + md_file)
                # md_file = "C:/Users/Aym_s/projects/github/profile/mds/blogs/numpy.md"
                html_file = md_file[:-2].replace("\\mds","")+"html"
                convert_md_to_html(md_file, html_file)