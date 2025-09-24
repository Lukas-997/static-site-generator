from enum import Enum, auto

class BlockType(Enum):
    PARAGRAPH = auto()
    HEADING = auto()
    ORDERED_LIST = auto()
    UNORDERED_LIST = auto()
    CODE = auto()
    QUOTE = auto()

def markdown_to_blocks(markdown: str):
    raw_blocks = markdown.split("\n\n")
    blocks = [block.strip() for block in raw_blocks if block.strip()]
    return blocks

def block_to_block_type(block: str):
    if block.startswith("#"):
        prefix = block.split(" ", 1)[0]
        if 1 <= len(prefix) <= 6 and all(ch == "#" for ch in prefix):
            return BlockType.HEADING
    if block.startswith("```") and block.endswith("```"):
        return BlockType.CODE

    lines = block.split("\n")

    # Quote block: every line starts with >
    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE

    # Unordered list: every line starts with "- "
    if all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST

    # Ordered list: every line must start with sequential number + ". "
    if all(line.lstrip().startswith(f"{i+1}. ") for i, line in enumerate(lines)):
        return BlockType.ORDERED_LIST

    # Otherwise: paragraph
    return BlockType.PARAGRAPH