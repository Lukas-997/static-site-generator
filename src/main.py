import os
import shutil
import sys
from copy_static import copy_static
from generate_page import generate_pages_recursive

def main():
    # basepath from CLI arg or default to "/"
    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"

    # for GitHub Pages, generate into docs/ instead of public/
    dest_dir = "docs"

    # clean destination
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)

    # copy static files
    copy_static("static", dest_dir)

    # recursively generate all pages
    generate_pages_recursive("content", "template.html", dest_dir, basepath)

if __name__ == "__main__":
    main()
