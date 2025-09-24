import os
import pathlib

from markdown_to_html import markdown_to_html_node
from extract_title import extract_title

def generate_page(from_path, template_path, dest_path, basepath="/"):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    # read markdown
    with open(from_path, "r", encoding="utf-8") as f:
        markdown_content = f.read()

    # read template
    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()

    # convert markdown -> HTML
    html_content = markdown_to_html_node(markdown_content).to_html()
    title = extract_title(markdown_content)

    # replace placeholders
    full_html = template_content.replace("{{ Title }}", title)
    full_html = full_html.replace("{{ Content }}", html_content)

    # adjust paths for GitHub Pages
    full_html = full_html.replace('href="/', f'href="{basepath}')
    full_html = full_html.replace('src="/', f'src="{basepath}')

    # ensure destination directory exists
    pathlib.Path(os.path.dirname(dest_path)).mkdir(parents=True, exist_ok=True)

    # write final file
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"Page generated: {dest_path}")

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath="/"):
    pathlib.Path(dest_dir_path).mkdir(parents=True, exist_ok=True)

    for entry in os.listdir(dir_path_content):
        content_path = os.path.join(dir_path_content, entry)
        dest_path = os.path.join(dest_dir_path, entry)

        if os.path.isfile(content_path) and content_path.endswith(".md"):
            html_dest_path = os.path.splitext(dest_path)[0] + ".html"
            generate_page(content_path, template_path, html_dest_path, basepath)
        elif os.path.isdir(content_path):
            generate_pages_recursive(content_path, template_path, dest_path, basepath)
