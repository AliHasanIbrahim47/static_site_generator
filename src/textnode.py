import re
from enum import Enum
from htmlnode import LeafNode, ParentNode

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
        if self.url:
            return f"TextNode({self.text}, {self.text_type.value}, {self.url})"
        else:
            return f"TextNode({self.text}, {self.text_type.value})"
    
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
        if len(parts) % 2 == 0:
            raise Exception(
                f"Invalid markdown syntax: unmatched delimiter {delimiter!r} in {old_node.text!r}"
            )

        split_nodes = []
        for i, part in enumerate(parts):
            if part == "":
                split_nodes.append(TextNode(part, TextType.TEXT))
            elif i % 2 == 1:
                split_nodes.append(TextNode(part, text_type))
            else:
                split_nodes.append(TextNode(part, TextType.TEXT))
        new_nodes.extend(split_nodes)

    return new_nodes

def split_nodes_image(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        text = old_node.text
        images = extract_markdown_images(text)

        if len(images) == 0:
            new_nodes.append(old_node)
            continue

        remaining_text = text

        for alt, url in images:
            image_markdown = f"![{alt}]({url})"
            sections = remaining_text.split(image_markdown, 1)

            if sections[0]:
                new_nodes.append(TextNode(sections[0], TextType.TEXT))

            new_nodes.append(TextNode(alt, TextType.IMAGE, url))
            remaining_text = sections[1]

        if remaining_text:
            new_nodes.append(TextNode(remaining_text, TextType.TEXT))

    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        text = old_node.text
        links = extract_markdown_links(text)

        if len(links) == 0:
            new_nodes.append(old_node)
            continue

        remaining_text = text

        for label, url in links:
            link_markdown = f"[{label}]({url})"
            sections = remaining_text.split(link_markdown, 1)

            if sections[0]:
                new_nodes.append(TextNode(sections[0], TextType.TEXT))

            new_nodes.append(TextNode(label, TextType.LINK, url))
            remaining_text = sections[1]

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

def block_to_block_type(block):
    if re.match(r"^#{1,6} .+", block):
        return BlockType.HEADING

    if block.startswith("```\n") and block.rstrip().endswith("```"):
        return BlockType.CODE

    lines = block.split("\n")

    if lines and all(line.startswith(">") for line in lines):
        return BlockType.QUOTE

    if lines and all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST

    if lines and all(line.startswith(f"{i + 1}. ") for i, line in enumerate(lines)):
        return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH

def text_to_children(text):
    """Convert inline markdown text to a list of HTMLNode children."""
    text = text.replace("\n", " ").strip()
    text_nodes = text_to_textnodes(text)
    filtered = [
        tn for tn in text_nodes
        if not (tn.text == "" and tn.text_type == TextType.TEXT)
    ]
    return [text_node_to_html_node(tn) for tn in filtered]


def heading_to_html_node(block):
    match = re.match(r"^(#{1,6}) (.*)", block)
    if match:
        level = len(match.group(1))
        heading_text = match.group(2).strip()
    else:
        level = 1
        heading_text = block
    return ParentNode(f"h{level}", text_to_children(heading_text))


def code_to_html_node(block):
    lines = block.splitlines()
    if len(lines) >= 2 and lines[0].startswith("```"):
        code_text = "\n".join(lines[1:-1])
        if not code_text.endswith("\n"):
            code_text = code_text + "\n"
    else:
        code_text = block

    code_leaf = text_node_to_html_node(TextNode(code_text, TextType.TEXT))
    return ParentNode("pre", [ParentNode("code", [code_leaf])])


def quote_to_html_node(block):
    lines = [re.sub(r"^>\s?", "", ln) for ln in block.splitlines()]
    quote_text = "\n".join(lines).strip()
    return ParentNode("blockquote", [ParentNode("p", text_to_children(quote_text))])


def unordered_list_to_html_node(block):
    items = []
    for line in block.splitlines():
        item_text = re.sub(r"^-\s+", "", line).strip()
        items.append(ParentNode("li", text_to_children(item_text)))
    return ParentNode("ul", items)


def ordered_list_to_html_node(block):
    items = []
    for line in block.splitlines():
        item_text = re.sub(r"^\d+\.\s+", "", line).strip()
        items.append(ParentNode("li", text_to_children(item_text)))
    return ParentNode("ol", items)


def paragraph_to_html_node(block):
    return ParentNode("p", text_to_children(block))


def extract_title(markdown: str) -> str:
    for line in markdown.split("\n"):
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped.lstrip("# ").strip()
    raise Exception("No h1 header found in markdown")


def markdown_to_html_node(markdown):
    markdown_blocks = markdown_to_blocks(markdown)
    children = []

    for block in markdown_blocks:
        if not block:
            continue

        block_type = block_to_block_type(block)

        if block_type == BlockType.HEADING:
            children.append(heading_to_html_node(block))
        elif block_type == BlockType.CODE:
            children.append(code_to_html_node(block))
        elif block_type == BlockType.QUOTE:
            children.append(quote_to_html_node(block))
        elif block_type == BlockType.UNORDERED_LIST:
            children.append(unordered_list_to_html_node(block))
        elif block_type == BlockType.ORDERED_LIST:
            children.append(ordered_list_to_html_node(block))
        else:
            p_children = text_to_children(block)
            if p_children:
                children.append(paragraph_to_html_node(block))

    return ParentNode("div", children)
