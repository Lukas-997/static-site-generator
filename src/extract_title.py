def extract_title(markdown: str) -> str:
    """
    Extract the first h1 (# heading) from the markdown text.
    If none is found, raise a ValueError.
    """
    for line in markdown.splitlines():
        line = line.strip()
        if line.startswith("# "):  # must be single '#' followed by space
            return line[2:].strip()
    raise ValueError("No h1 header found in markdown")
