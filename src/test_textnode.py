import unittest

from textnode import *

class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.ITALIC)
        self.assertNotEqual(node, node2)
        node = TextNode("This is a text node", TextType.BOLD, "https://www.boot.dev")
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")
    
    def test_split_nodes_delimiter(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(new_nodes, [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" word", TextType.TEXT),
        ])

    def test_split_nodes_delimiter_unmatched(self):
        node = TextNode("This has **unmatched bold", TextType.TEXT)
        with self.assertRaises(Exception) as ctx:
            split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertIn("unmatched delimiter", str(ctx.exception))

    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_images_multiple(self):
        text = (
            "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) "
            "and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        )
        self.assertListEqual(
            [
                ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
                ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg"),
            ],
            extract_markdown_images(text),
        )

    def test_extract_markdown_images_none(self):
        self.assertListEqual([], extract_markdown_images("No images here, just text."))

    def test_extract_markdown_links(self):
        text = (
            "This is text with a link [to boot dev](https://www.boot.dev) "
            "and [to youtube](https://www.youtube.com/@bootdotdev)"
        )
        self.assertListEqual(
            [
                ("to boot dev", "https://www.boot.dev"),
                ("to youtube", "https://www.youtube.com/@bootdotdev"),
            ],
            extract_markdown_links(text),
        )

    def test_extract_markdown_links_single(self):
        matches = extract_markdown_links("[click me](https://example.com)")
        self.assertListEqual([("click me", "https://example.com")], matches)

    def test_extract_markdown_links_none(self):
        self.assertListEqual([], extract_markdown_links("No links here."))

    def test_extract_markdown_links_ignores_images(self):
        text = "An image ![alt](https://img.com/a.png) and a [link](https://example.com)"
        self.assertListEqual([("link", "https://example.com")], extract_markdown_links(text))
        self.assertListEqual([("alt", "https://img.com/a.png")], extract_markdown_images(text))

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
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_images_single(self):
        node = TextNode("![only image](https://example.com/img.png)", TextType.TEXT)
        self.assertListEqual(
            [TextNode("only image", TextType.IMAGE, "https://example.com/img.png")],
            split_nodes_image([node]),
        )

    def test_split_images_no_images(self):
        node = TextNode("plain text with no images", TextType.TEXT)
        self.assertListEqual([node], split_nodes_image([node]))

    def test_split_images_at_boundaries(self):
        node = TextNode(
            "![start](https://a.com) middle text ![end](https://b.com)",
            TextType.TEXT,
        )
        self.assertListEqual(
            [
                TextNode("start", TextType.IMAGE, "https://a.com"),
                TextNode(" middle text ", TextType.TEXT),
                TextNode("end", TextType.IMAGE, "https://b.com"),
            ],
            split_nodes_image([node]),
        )

    def test_split_images_non_text_passthrough(self):
        bold = TextNode("not plain text", TextType.BOLD)
        self.assertListEqual([bold], split_nodes_image([bold]))

    def test_split_images_multiple_input_nodes(self):
        node1 = TextNode("before ![a](https://a.com)", TextType.TEXT)
        node2 = TextNode("plain", TextType.TEXT)
        node3 = TextNode("bold", TextType.BOLD)
        self.assertListEqual(
            [
                TextNode("before ", TextType.TEXT),
                TextNode("a", TextType.IMAGE, "https://a.com"),
                node2,
                node3,
            ],
            split_nodes_image([node1, node2, node3]),
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
                TextNode(
                    "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
                ),
            ],
            new_nodes,
        )

    def test_split_links_single(self):
        node = TextNode("[click me](https://example.com)", TextType.TEXT)
        self.assertListEqual(
            [TextNode("click me", TextType.LINK, "https://example.com")],
            split_nodes_link([node]),
        )

    def test_split_links_no_links(self):
        node = TextNode("plain text with no links", TextType.TEXT)
        self.assertListEqual([node], split_nodes_link([node]))

    def test_split_links_at_boundaries(self):
        node = TextNode(
            "[start](https://a.com) middle text [end](https://b.com)",
            TextType.TEXT,
        )
        self.assertListEqual(
            [
                TextNode("start", TextType.LINK, "https://a.com"),
                TextNode(" middle text ", TextType.TEXT),
                TextNode("end", TextType.LINK, "https://b.com"),
            ],
            split_nodes_link([node]),
        )

    def test_split_links_non_text_passthrough(self):
        italic = TextNode("not plain text", TextType.ITALIC)
        self.assertListEqual([italic], split_nodes_link([italic]))

    def test_split_links_ignores_image_syntax(self):
        node = TextNode(
            "An image ![alt](https://img.com/a.png) and a [link](https://example.com)",
            TextType.TEXT,
        )
        self.assertListEqual(
            [
                TextNode("An image ![alt](https://img.com/a.png) and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://example.com"),
            ],
            split_nodes_link([node]),
        )

    def test_text_to_textnodes(self):
        text = (
            "This is **text** with an _italic_ word and a `code block` and an "
            "![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        )
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode(
                    "obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"
                ),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            text_to_textnodes(text),
        )

    def test_text_to_textnodes_plain(self):
        self.assertListEqual(
            [TextNode("plain text only", TextType.TEXT)],
            text_to_textnodes("plain text only"),
        )

    def test_block_to_block_type_heading(self):
        self.assertEqual(BlockType.HEADING, block_to_block_type("# Heading 1"))
        self.assertEqual(BlockType.HEADING, block_to_block_type("###### Heading 6"))
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type("#No space"))
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type("####### Too many"))

    def test_block_to_block_type_code(self):
        block = "```\ncode line 1\ncode line 2\n```"
        self.assertEqual(BlockType.CODE, block_to_block_type(block))
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type("```inline code```"))

    def test_block_to_block_type_quote(self):
        self.assertEqual(
            BlockType.QUOTE,
            block_to_block_type("> quote line 1\n> quote line 2"),
        )
        self.assertEqual(BlockType.QUOTE, block_to_block_type(">no space after"))
        self.assertEqual(
            BlockType.PARAGRAPH,
            block_to_block_type("> quote line 1\nnot a quote"),
        )

    def test_block_to_block_type_unordered_list(self):
        self.assertEqual(
            BlockType.UNORDERED_LIST,
            block_to_block_type("- item 1\n- item 2"),
        )
        self.assertEqual(BlockType.UNORDERED_LIST, block_to_block_type("- single item"))
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type("-no space"))

    def test_block_to_block_type_ordered_list(self):
        self.assertEqual(
            BlockType.ORDERED_LIST,
            block_to_block_type("1. first\n2. second\n3. third"),
        )
        self.assertEqual(BlockType.ORDERED_LIST, block_to_block_type("1. only item"))
        self.assertEqual(
            BlockType.PARAGRAPH,
            block_to_block_type("1. first\n3. skipped"),
        )

    def test_block_to_block_type_paragraph(self):
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type("Just a paragraph."))
        self.assertEqual(
            BlockType.PARAGRAPH,
            block_to_block_type("Line one\nLine two"),
        )

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

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_headings(self):
        md = "# Heading 1\n\n## Heading 2\n\n###### Heading 6"
        html = markdown_to_html_node(md).to_html()
        self.assertEqual(
            html,
            "<div><h1>Heading 1</h1><h2>Heading 2</h2><h6>Heading 6</h6></div>",
        )

    def test_heading_with_inline(self):
        md = "# Title with **bold**"
        html = markdown_to_html_node(md).to_html()
        self.assertEqual(html, "<div><h1>Title with <b>bold</b></h1></div>")

    def test_blockquote(self):
        md = "> This is a quote\n> with **bold** text"
        html = markdown_to_html_node(md).to_html()
        self.assertEqual(
            html,
            "<div><blockquote><p>This is a quote with <b>bold</b> text</p></blockquote></div>",
        )

    def test_unordered_list(self):
        md = "- item one\n- item **two**"
        html = markdown_to_html_node(md).to_html()
        self.assertEqual(
            html,
            "<div><ul><li>item one</li><li>item <b>two</b></li></ul></div>",
        )

    def test_ordered_list(self):
        md = "1. first\n2. second with _italic_"
        html = markdown_to_html_node(md).to_html()
        self.assertEqual(
            html,
            "<div><ol><li>first</li><li>second with <i>italic</i></li></ol></div>",
        )

    def test_inline_link_and_image(self):
        md = "A [link](https://boot.dev) and ![img](https://example.com/a.png)"
        html = markdown_to_html_node(md).to_html()
        self.assertEqual(
            html,
            '<div><p>A <a href="https://boot.dev">link</a> and <img src="https://example.com/a.png" alt="img"></p></div>',
        )

    def test_extract_title(self):
        self.assertEqual("Hello", extract_title("# Hello"))
        self.assertEqual("Hello", extract_title("  # Hello  "))
        self.assertEqual("Tolkien Fan Club", extract_title("# Tolkien Fan Club\n\nSome content"))

    def test_extract_title_ignores_h2(self):
        md = "## Not the title\n\n# The Real Title"
        self.assertEqual("The Real Title", extract_title(md))

    def test_extract_title_raises(self):
        with self.assertRaises(Exception) as ctx:
            extract_title("No heading here")
        self.assertIn("No h1 header", str(ctx.exception))

if __name__ == "__main__":
    unittest.main()