import re
import unittest

def extract_markdown_images(text):
    """
    Extract markdown image tags: ![alt](url)
    Returns list of tuples: (alt_text, url)
    """
    pattern = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
    return re.findall(pattern, text)


def extract_markdown_links(text):
    """
    Extract markdown links: [text](url)
    Returns list of tuples: (anchor_text, url)
    """
    pattern = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"
    return re.findall(pattern, text)
