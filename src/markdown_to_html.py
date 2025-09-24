from markdown_block import BlockType, block_to_block_type, markdown_to_blocks
from textnode import text_to_textnodes
from textnode_to_html import text_node_to_html_node
from htmlnode import ParentNode, LeafNode

def markdown_to_html_node(markdown: str):
    blocks = markdown_to_blocks(markdown)
    children = []

    for block in blocks:
        block_type = block_to_block_type(block)

        if block_type == BlockType.PARAGRAPH:
            # Wrap text children inside <p>
            if block_type == BlockType.PARAGRAPH:
                normalized = block.replace("\n", " ")
                inline_children = [text_node_to_html_node(n) for n in text_to_textnodes(normalized)]
                children.append(ParentNode("p", inline_children))

        elif block_type == BlockType.HEADING:
            # Count how many # at start
            heading_level = len(block.split(" ", 1)[0])
            heading_text = block[heading_level + 1 :] if len(block.split(" ", 1)) > 1 else ""
            inline_children = [text_node_to_html_node(n) for n in text_to_textnodes(heading_text)]
            children.append(ParentNode(f"h{heading_level}", inline_children))

        elif block_type == BlockType.CODE:
            # Strip backticks, don’t parse inline markdown
            inner = block.strip("`").strip()
            code_node = LeafNode("code", inner)
            children.append(ParentNode("pre", [code_node]))

        elif block_type == BlockType.QUOTE:
            # Remove leading ">" from each line
            quote_text = "\n".join(line.lstrip("> ") for line in block.split("\n"))
            inline_children = [text_node_to_html_node(n) for n in text_to_textnodes(quote_text)]
            children.append(ParentNode("blockquote", inline_children))

        elif block_type == BlockType.UNORDERED_LIST:
            list_items = []
            for line in block.split("\n"):
                item_text = line[2:]  # remove "- "
                inline_children = [text_node_to_html_node(n) for n in text_to_textnodes(item_text)]
                list_items.append(ParentNode("li", inline_children))
            children.append(ParentNode("ul", list_items))

        elif block_type == BlockType.ORDERED_LIST:
            list_items = []
            for line in block.split("\n"):
                # remove "1. ", "2. ", etc.
                _, item_text = line.split(". ", 1)
                inline_children = [text_node_to_html_node(n) for n in text_to_textnodes(item_text)]
                list_items.append(ParentNode("li", inline_children))
            children.append(ParentNode("ol", list_items))

        else:
            # fallback (shouldn’t happen)
            inline_children = [text_node_to_html_node(n) for n in text_to_textnodes(block)]
            children.append(ParentNode("p", inline_children))

    return ParentNode("div", children)
