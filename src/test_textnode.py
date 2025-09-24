import unittest
import extract_title
from markdown_block import BlockType, block_to_block_type, markdown_to_blocks
from markdown_to_html import markdown_to_html_node
from regex import extract_markdown_images, extract_markdown_links
from textnode import TextNode, TextType, text_to_textnodes
from htmlnode import HTMLNode
from htmlnode import LeafNode
from htmlnode import ParentNode 
from textnode_to_html import text_node_to_html_node
from split_nodes_delimiter import split_nodes_delimiter, split_nodes_image, split_nodes_link


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_textnodes_are_equal(self):
        node1 = TextNode("Hello", TextType.BOLD, "https://example.com")
        node2 = TextNode("Hello", TextType.BOLD, "https://example.com")
        self.assertEqual(node1, node2)

    def test_textnodes_different_text(self):
        node1 = TextNode("Hello", TextType.BOLD, "https://example.com")
        node2 = TextNode("Hi", TextType.BOLD, "https://example.com")
        self.assertNotEqual(node1, node2)

    def test_textnodes_different_text_type(self):
        node1 = TextNode("Hello", TextType.BOLD, "https://example.com")
        node2 = TextNode("Hello", TextType.ITALIC, "https://example.com")
        self.assertNotEqual(node1, node2)

    def test_textnodes_url_none(self):
        node1 = TextNode("Hello", TextType.BOLD, None)
        node2 = TextNode("Hello", TextType.BOLD, None)
        self.assertEqual(node1, node2)

    def test_textnodes_different_url(self):
        node1 = TextNode("Hello", TextType.BOLD, "https://example.com")
        node2 = TextNode("Hello", TextType.BOLD, "https://another.com")
        self.assertNotEqual(node1, node2)

    def test_repr_format(self):
        node = TextNode("Hello", TextType.BOLD, "https://example.com")
        expected = "TextNode(Hello, bold, https://example.com)"
        self.assertEqual(repr(node), expected)


class TestHTMLNode(unittest.TestCase):
    def test_props_to_html_with_attributes(self):
        node = HTMLNode(
            tag="a",
            value="Google",
            props={"href": "https://www.google.com", "target": "_blank"}
        )
        self.assertEqual(
            node.props_to_html(),
            ' href="https://www.google.com" target="_blank"'
        )

    def test_props_to_html_no_attributes(self):
        node = HTMLNode(tag="p", value="Hello")
        self.assertEqual(node.props_to_html(), "")

    def test_repr_output(self):
        node = HTMLNode(
            tag="p",
            value="Hello World",
            props={"class": "text-bold"}
        )
        expected_repr = "HTMLNode(tag=p, value=Hello World, children=None, props={'class': 'text-bold'})"
        self.assertEqual(repr(node), expected_repr)        


class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_with_props(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        self.assertEqual(
            node.to_html(),
            '<a href="https://www.google.com">Click me!</a>'
        )

    def test_leaf_to_html_raw_text(self):
        node = LeafNode(None, "Just text")
        self.assertEqual(node.to_html(), "Just text")

    def test_leaf_no_value_raises(self):
        with self.assertRaises(ValueError):
            LeafNode("p", None)

class TestParentNode(unittest.TestCase):
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_mixed_children_raw_and_tagged(self):
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )
        self.assertEqual(
            node.to_html(),
            "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>",
        )

    def test_missing_tag_raises(self):
        with self.assertRaises(ValueError) as cm:
            ParentNode(None, [LeafNode("span", "x")]).to_html()
        self.assertIn("tag", str(cm.exception))

    def test_missing_children_raises(self):
        with self.assertRaises(ValueError) as cm:
            ParentNode("div", None).to_html()
        self.assertIn("children", str(cm.exception))

    def test_empty_children_ok(self):
        node = ParentNode("div", [])
        self.assertEqual(node.to_html(), "<div></div>")

    def test_props_render(self):
        node = ParentNode("div", [LeafNode("span", "x")], {"class": "wrapper"})
        self.assertEqual(node.to_html(), '<div class="wrapper"><span>x</span></div>')

    class TestTextNodeToHTML(unittest.TestCase):
        def test_text(self):
            node = TextNode("This is a text node", TextType.TEXT)
            html_node = text_node_to_html_node(node)
            self.assertEqual(html_node.tag, None)
            self.assertEqual(html_node.value, "This is a text node")

        def test_bold(self):
            node = TextNode("boldy", TextType.BOLD)
            html_node = text_node_to_html_node(node)
            self.assertEqual(html_node.tag, "b")
            self.assertEqual(html_node.value, "boldy")
            self.assertEqual(html_node.to_html(), "<b>boldy</b>")

        def test_italic(self):
            node = TextNode("slant", TextType.ITALIC)
            html_node = text_node_to_html_node(node)
            self.assertEqual(html_node.tag, "i")
            self.assertEqual(html_node.to_html(), "<i>slant</i>")

        def test_code(self):
            node = TextNode("print('x')", TextType.CODE)
            html_node = text_node_to_html_node(node)
            self.assertEqual(html_node.tag, "code")
            self.assertEqual(html_node.to_html(), "<code>print('x')</code>")

        def test_link(self):
            node = TextNode("Click me", TextType.LINK, "https://example.com")
            html_node = text_node_to_html_node(node)
            self.assertEqual(html_node.tag, "a")
            self.assertEqual(html_node.value, "Click me")
            self.assertEqual(html_node.props, {"href": "https://example.com"})
            self.assertEqual(html_node.to_html(), '<a href="https://example.com">Click me</a>')

        def test_image(self):
            node = TextNode("alt text", TextType.IMAGE, "https://img.example/x.png")
            html_node = text_node_to_html_node(node)
            self.assertEqual(html_node.tag, "img")
            self.assertEqual(html_node.value, "")
            self.assertEqual(html_node.props, {"src": "https://img.example/x.png", "alt": "alt text"})
            self.assertEqual(
                html_node.to_html(),
                '<img src="https://img.example/x.png" alt="alt text"></img>'
            )

        def test_unsupported_type_raises(self):
            class Weird:
                text = "x"
                text_type = "NOPE"
                url = None

            with self.assertRaises(ValueError):
                text_node_to_html_node(Weird())

def test_code_delimiter():
    node = TextNode("This is text with a `code block` word", TextType.TEXT)
    result = split_nodes_delimiter([node], "`", TextType.CODE)
    expected = [
        TextNode("This is text with a ", TextType.TEXT),
        TextNode("code block", TextType.CODE),
        TextNode(" word", TextType.TEXT),
    ]
    assert result == expected


def test_bold_delimiter():
    node = TextNode("This is **bold** text", TextType.TEXT)
    result = split_nodes_delimiter([node], "**", TextType.BOLD)
    expected = [
        TextNode("This is ", TextType.TEXT),
        TextNode("bold", TextType.BOLD),
        TextNode(" text", TextType.TEXT),
    ]
    assert result == expected


def test_italic_delimiter():
    node = TextNode("This is _italic_ text", TextType.TEXT)
    result = split_nodes_delimiter([node], "_", TextType.ITALIC)
    expected = [
        TextNode("This is ", TextType.TEXT),
        TextNode("italic", TextType.ITALIC),
        TextNode(" text", TextType.TEXT),
    ]
    assert result == expected


def test_multiple_delimiters():
    node = TextNode("Normal `code` and **bold** together", TextType.TEXT)
    result = split_nodes_delimiter([node], "`", TextType.CODE)
    result = split_nodes_delimiter(result, "**", TextType.BOLD)
    expected = [
        TextNode("Normal ", TextType.TEXT),
        TextNode("code", TextType.CODE),
        TextNode(" and ", TextType.TEXT),
        TextNode("bold", TextType.BOLD),
        TextNode(" together", TextType.TEXT),
    ]
    assert result == expected


def test_unmatched_delimiter():
    node = TextNode("This is `unmatched code", TextType.TEXT)
    try:
        split_nodes_delimiter([node], "`", TextType.CODE)
    except ValueError as e:
        assert "Unmatched delimiter" in str(e)
    else:
        assert False, "Expected ValueError for unmatched delimiter"

class TestMarkdownExtractors(unittest.TestCase):

    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual(
            [("image", "https://i.imgur.com/zjjcJKZ.png")],
            matches
        )

    def test_extract_multiple_images(self):
        text = "![one](http://a.com/1.png) and ![two](http://a.com/2.png)"
        matches = extract_markdown_images(text)
        self.assertListEqual(
            [("one", "http://a.com/1.png"), ("two", "http://a.com/2.png")],
            matches
        )

    def test_extract_markdown_links(self):
        matches = extract_markdown_links(
            "This is text with a [boot dev](https://www.boot.dev)"
        )
        self.assertListEqual(
            [("boot dev", "https://www.boot.dev")],
            matches
        )

    def test_extract_multiple_links(self):
        text = "[google](https://google.com) and [github](https://github.com)"
        matches = extract_markdown_links(text)
        self.assertListEqual(
            [("google", "https://google.com"), ("github", "https://github.com")],
            matches
        )

    def test_mixed_images_and_links(self):
        text = "![pic](http://img.com/x.png) and [ref](http://ref.com)"
        img_matches = extract_markdown_images(text)
        link_matches = extract_markdown_links(text)
        self.assertListEqual([("pic", "http://img.com/x.png")], img_matches)
        self.assertListEqual([("ref", "http://ref.com")], link_matches)

    def test_no_matches(self):
        self.assertEqual([], extract_markdown_images("no images here"))
        self.assertEqual([], extract_markdown_links("just plain text"))

class TestSplitNodes(unittest.TestCase):

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
            ],
            new_nodes,
        )

    def test_split_links(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode("to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"),
            ],
            new_nodes,
        )

    def test_no_images(self):
        node = TextNode("plain text no images", TextType.TEXT)
        self.assertListEqual([node], split_nodes_image([node]))

    def test_no_links(self):
        node = TextNode("plain text no links", TextType.TEXT)
        self.assertListEqual([node], split_nodes_link([node]))

    def test_non_text_nodes(self):
        node = TextNode("not text", TextType.IMAGE, "http://x.com/pic.png")
        self.assertListEqual([node], split_nodes_image([node]))
        self.assertListEqual([node], split_nodes_link([node]))

    def test_empty_text_segments(self):
        node = TextNode("![alt](http://a.com/img.png)", TextType.TEXT)
        result = split_nodes_image([node])
        self.assertListEqual(
            [TextNode("alt", TextType.IMAGE, "http://a.com/img.png")],
            result
        )

    def test_mixed_images_and_text(self):
        node = TextNode("start ![a](http://a.com) middle ![b](http://b.com) end", TextType.TEXT)
        result = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("start ", TextType.TEXT),
                TextNode("a", TextType.IMAGE, "http://a.com"),
                TextNode(" middle ", TextType.TEXT),
                TextNode("b", TextType.IMAGE, "http://b.com"),
                TextNode(" end", TextType.TEXT),
            ],
            result
        )

class TestTextToTextNodes(unittest.TestCase):
    def test_basic_text(self):
        text = "Just plain text"
        result = text_to_textnodes(text)
        expected = [TextNode("Just plain text", TextType.TEXT)]
        self.assertEqual(result, expected)

    def test_bold(self):
        text = "This is **bold**"
        result = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
        ]
        self.assertEqual(result, expected)

    def test_italic_and_code(self):
        text = "word with _italic_ and `code`"
        result = text_to_textnodes(text)
        expected = [
            TextNode("word with ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" and ", TextType.TEXT),
            TextNode("code", TextType.CODE),
        ]
        self.assertEqual(result, expected)

    def test_image(self):
        text = "here is ![alt](http://img.com/x.png)"
        result = text_to_textnodes(text)
        expected = [
            TextNode("here is ", TextType.TEXT),
            TextNode("alt", TextType.IMAGE, "http://img.com/x.png"),
        ]
        self.assertEqual(result, expected)

    def test_link(self):
        text = "visit [site](http://site.com)"
        result = text_to_textnodes(text)
        expected = [
            TextNode("visit ", TextType.TEXT),
            TextNode("site", TextType.LINK, "http://site.com"),
        ]
        self.assertEqual(result, expected)

    def test_full_example(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        result = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        self.assertEqual(result, expected)

class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_leading_and_trailing_whitespace(self):
        md = "   \n\n   First block   \n\n   Second block   \n\n"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["First block", "Second block"])

    def test_multiple_blank_lines(self):
        md = "Paragraph one\n\n\n\nParagraph two"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["Paragraph one", "Paragraph two"])

    def test_single_block(self):
        md = "Only one block, no splitting here"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["Only one block, no splitting here"])

    def test_empty_string(self):
        md = ""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])

class TestBlockToBlockType(unittest.TestCase):
    def test_heading_levels(self):
        self.assertEqual(block_to_block_type("# Heading"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("###### Heading 6"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("####### Not heading"), BlockType.PARAGRAPH)

    def test_code_block(self):
        block = "```\nprint('hello')\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_quote_block(self):
        block = "> This is a quote\n> With another line"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_unordered_list(self):
        block = "- Item 1\n- Item 2\n- Item 3"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_ordered_list_valid(self):
        block = "1. First\n2. Second\n3. Third"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_ordered_list_invalid(self):
        block = "1. First\n3. Skips second"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_paragraph(self):
        block = "This is just a plain paragraph with some text."
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_mixed_list_invalid(self):
        block = "1. First\n- Not matching"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_single_line_unordered(self):
        block = "- Only one item"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_single_line_ordered(self):
        block = "1. Only one item"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

class TestMarkdownToHTMLNode(unittest.TestCase):
    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

class TestExtractTitle(unittest.TestCase):
    def test_simple_title(self):
        self.assertEqual(extract_title("# Hello"), "Hello")

    def test_title_with_extra_spaces(self):
        self.assertEqual(extract_title("   #   My Title   "), "My Title")

    def test_multiline_document(self):
        md = """
# First Title

Some paragraph text

## Subheading

More text
"""
        self.assertEqual(extract_title(md), "First Title")

    def test_no_h1_raises(self):
        md = "## Subheading only\nSome text"
        with self.assertRaises(ValueError):
            extract_title(md)

    def test_ignores_h2_and_h3(self):
        md = """
## Wrong
### Wrong again
# Correct Title
"""
        self.assertEqual(extract_title(md), "Correct Title")

    def test_title_with_inline_formatting(self):
        md = "# Hello **World**"
        self.assertEqual(extract_title(md), "Hello **World**")

    def test_codeblock(self):
        md = """
if __name__ == "__main__":
    unittest.main()
```"""
        self.assertEqual(extract_title(md), "if __name__ == \"__main__\":")