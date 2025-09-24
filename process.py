import os
from bs4 import BeautifulSoup

def update_html_titles(root_dir=''):
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith('.html'):
                full_path = os.path.join(dirpath, filename)
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        soup = BeautifulSoup(f, 'html.parser')

                    h1_tag = soup.find('h1')
                    if h1_tag and h1_tag.string:
                        new_title = h1_tag.string.strip()

                        if soup.title:
                            soup.title.string.replace_with(new_title)
                        else:
                            # Create <title> if missing
                            head = soup.head or soup.new_tag('head')
                            title_tag = soup.new_tag('title')
                            title_tag.string = new_title
                            head.insert(0, title_tag)
                            if not soup.head:
                                soup.insert(0, head)

                        with open(full_path, 'w', encoding='utf-8') as f:
                            f.write(str(soup))
                        print(f"Updated title to {new_title} in: {full_path}")
                    else:
                        print(f"No <h1> found in: {full_path}")
                        if soup.title:
                            soup.title.string.replace_with("Page")
                            
                    # 1) Remove all <script> tags and their contents
                    for script in soup.find_all('script'):
                        script.decompose()

                    # 2) Ensure there’s a <head> to work with
                    head = soup.head
                    if head is None:
                        head = soup.new_tag('head')
                        # Insert head before the first element under <html>, or at top
                        if soup.html:
                            soup.html.insert(0, head)
                        else:
                            soup.insert(0, head)

                    # 3) Add the stylesheet link
                    link_tag = soup.new_tag(
                        'link',
                        rel='stylesheet',
                        href='../styles.css'
                    )
                    head.append(link_tag)

                except Exception as e:
                    print(f"Error processing {full_path}: {e}")


if __name__ == "__main__":
    update_html_titles("C:/Users/Aym_s/projects/github/profile")
    input("\n Press Enter to exit")