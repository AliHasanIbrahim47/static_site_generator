import re
from enum import Enum
from htmlnode import LeafNode
from htmlnode import ParentNode, LeafNode

class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"

class TextNode():
    def __init__(self, text, text_type, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, value):
        if self.text == value.text and self.text_type == value.text_type and self.url == value.url:
            return True
        return False
    
    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"
    
def text_node_to_html_node(text_node):
    if text_node.text_type == TextType.TEXT:
        return LeafNode(None, text_node.text)
    if text_node.text_type == TextType.BOLD:
        return LeafNode("b", text_node.text)
    if text_node.text_type == TextType.ITALIC:
        return LeafNode("i", text_node.text)
    if text_node.text_type == TextType.CODE:
        return LeafNode("code", text_node.text)
    if text_node.text_type == TextType.LINK:
        return LeafNode("a", text_node.text, {"href": f"{text_node.url}"})
    if text_node.text_type == TextType.IMAGE:
        return LeafNode("img", "", {"src": f"{text_node.url}", "alt": f"{text_node.text}"})
    raise Exception("Use one of the provided text types")

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        parts = old_node.text.split(delimiter)
        for i, part in enumerate(parts):
            if part == "":
                new_nodes.append(TextNode(part, TextType.TEXT))
            elif i % 2 == 1:
                new_nodes.append(TextNode(part, text_type))
            else:
                new_nodes.append(TextNode(part, TextType.TEXT))

    return new_nodes

def split_nodes_image(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        text = old_node.text
        images = extract_markdown_images(text)

        if len(images) == 0:
            new_nodes.append(old_node)
            continue

        remaining_text = text

        for alt, url in images:
            image_markdown = f"![{alt}]({url})"

            before, after = remaining_text.split(image_markdown, 1)

            if before:
                new_nodes.append(TextNode(before, TextType.TEXT))

            new_nodes.append(TextNode(alt, TextType.IMAGE, url))

            remaining_text = after

        if remaining_text:
            new_nodes.append(TextNode(remaining_text, TextType.TEXT))

    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        text = old_node.text
        links = extract_markdown_links(text)

        if len(links) == 0:
            new_nodes.append(old_node)
            continue

        remaining_text = text

        for label, url in links:
            link_markdown = f"[{label}]({url})"

            before, after = remaining_text.split(link_markdown, 1)

            if before:
                new_nodes.append(TextNode(before, TextType.TEXT))

            new_nodes.append(TextNode(label, TextType.LINK, url))

            remaining_text = after

        if remaining_text:
            new_nodes.append(TextNode(remaining_text, TextType.TEXT))

    return new_nodes

def extract_markdown_images(text):
    matches = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches

def extract_markdown_links(text):
    matches = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches

def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]

    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)

    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)

    return nodes

def markdown_to_blocks(text):
    split_list = text.split("\n\n")
    result_list = []
    for item in split_list:
        result_list.append(item.strip())
    return result_list

def block_to_block_type(text):
    if text.startswith("#"):
        return BlockType.HEADING
    elif text.startswith("```"):
        return BlockType.CODE
    elif text.startswith(">"):
        return BlockType.QUOTE
    elif text.startswith("- "):
        return BlockType.UNORDERED_LIST
    elif bool(re.match(r"\d+\.\s", text)):
        return BlockType.ORDERED_LIST
    else:
        return BlockType.PARAGRAPH

def markdown_to_html_node(markdown):
    markdown_blocks = markdown_to_blocks(markdown)

    def text_to_children(text):
        """Convert inline markdown text to a list of HTMLNode children."""
        # collapse internal newlines into spaces for inline parsing
        text = text.replace("\n", " ").strip()
        text_nodes = text_to_textnodes(text)
        # filter out empty plain text nodes to avoid creating LeafNodes with empty values
        filtered = [tn for tn in text_nodes if not (tn.text == "" and tn.text_type == TextType.TEXT)]
        return [text_node_to_html_node(tn) for tn in filtered]

    children = []

    for block in markdown_blocks:
        block_type = block_to_block_type(block)

        if block_type == BlockType.HEADING:
            # count leading # characters
            match = re.match(r"^(#{1,6})\s*(.*)", block)
            if match:
                level = min(6, len(match.group(1)))
                heading_text = match.group(2).strip()
            else:
                level = 1
                heading_text = block

            node = ParentNode(f"h{level}", text_to_children(heading_text))
            children.append(node)

        elif block_type == BlockType.CODE:
            # strip the surrounding ``` lines
            lines = block.splitlines()
            if len(lines) >= 2 and lines[0].startswith("```"):
                # take everything between the fence lines
                code_text = "\n".join(lines[1:-1])
                # ensure trailing newline as tests expect
                if not code_text.endswith("\n"):
                    code_text = code_text + "\n"
            else:
                code_text = block

            # code block should not be inline-parsed
            code_leaf = LeafNode(None, code_text)
            code_node = ParentNode("code", [code_leaf])
            pre_node = ParentNode("pre", [code_node])
            children.append(pre_node)

        elif block_type == BlockType.QUOTE:
            # remove leading '>' characters and wrap in blockquote
            lines = [re.sub(r"^>\s?", "", ln) for ln in block.splitlines()]
            quote_text = "\n".join(lines).strip()
            p_children = text_to_children(quote_text)
            if p_children:
                p_node = ParentNode("p", p_children)
                blockquote_node = ParentNode("blockquote", [p_node])
                children.append(blockquote_node)

        elif block_type == BlockType.UNORDERED_LIST:
            # split lines and create <ul> with <li>
            items = []
            for line in block.splitlines():
                item_text = re.sub(r"^[-]\s+", "", line).strip()
                li_children = text_to_children(item_text)
                items.append(ParentNode("li", li_children))
            ul = ParentNode("ul", items)
            children.append(ul)

        elif block_type == BlockType.ORDERED_LIST:
            items = []
            for line in block.splitlines():
                item_text = re.sub(r"^\d+\.\s+", "", line).strip()
                li_children = text_to_children(item_text)
                items.append(ParentNode("li", li_children))
            ol = ParentNode("ol", items)
            children.append(ol)

        else:
            # paragraph
            p_children = text_to_children(block)
            if p_children:
                p_node = ParentNode("p", p_children)
                children.append(p_node)

    return ParentNode("div", children)
