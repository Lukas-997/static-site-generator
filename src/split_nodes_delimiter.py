from enum import Enum, auto
import re
from textnode import TextNode, TextType


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        parts = node.text.split(delimiter)

        if len(parts) == 1:
            new_nodes.append(node)
            continue

        if len(parts) % 2 == 0:
            raise ValueError(f"Unmatched delimiter '{delimiter}' in text: {node.text}")

        for i, part in enumerate(parts):
            if part == "":
                continue
            if i % 2 == 0:  # outside delimiters
                new_nodes.append(TextNode(part, TextType.TEXT))
            else:          # inside delimiters
                new_nodes.append(TextNode(part, text_type))

    return new_nodes



def split_nodes_image(old_nodes):
    new_nodes = []
    pattern = re.compile(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)")

    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        text = node.text
        last_index = 0
        for match in pattern.finditer(text):
            start, end = match.span()
            alt, url = match.groups()

            # text before the image
            if start > last_index:
                new_nodes.append(TextNode(text[last_index:start], TextType.TEXT))

            # the image node
            new_nodes.append(TextNode(alt, TextType.IMAGE, url))

            last_index = end

        # trailing text
        if last_index < len(text):
            new_nodes.append(TextNode(text[last_index:], TextType.TEXT))

    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []
    pattern = re.compile(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)")

    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        text = node.text
        last_index = 0
        for match in pattern.finditer(text):
            start, end = match.span()
            anchor, url = match.groups()

            # text before the link
            if start > last_index:
                new_nodes.append(TextNode(text[last_index:start], TextType.TEXT))

            # the link node
            new_nodes.append(TextNode(anchor, TextType.LINK, url))

            last_index = end

        # trailing text
        if last_index < len(text):
            new_nodes.append(TextNode(text[last_index:], TextType.TEXT))

    return new_nodes