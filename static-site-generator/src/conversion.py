from textnode import TextNode
from htmlnode import HTMLNode, LeafNode
import re

TEXT_TYPE_TEXT = "text"
TEXT_TYPE_BOLD = "bold"
TEXT_TYPE_ITALIC = "italic"
TEXT_TYPE_CODE = "code"
TEXT_TYPE_LINK = "link"
TEXT_TYPE_IMAGE = "image"

def text_node_to_html_node(text_node):
    if not isinstance(text_node, TextNode):
        raise TypeError("Expected a TextNode instance")
    
    text_type = text_node.text_type

    if text_type == TEXT_TYPE_TEXT:
        return LeafNode(value=text_node.text, tag=None)
    
    if text_type == TEXT_TYPE_BOLD:
        return LeafNode(value=text_node.text, tag="b")
    
    if text_type == TEXT_TYPE_ITALIC:
        return LeafNode(value=text_node.text, tag="i")
    
    if text_type == TEXT_TYPE_CODE:
        return LeafNode(value=text_node.text, tag="code")
    
    if text_type == TEXT_TYPE_LINK:
        return LeafNode(value=text_node.text, tag="a", props={"href": text_node.url})
    
    if text_type == TEXT_TYPE_IMAGE:
        return LeafNode(value="", tag="img", props={"src": text_node.url, "alt": text_node.text})
    
    else:
        raise ValueError(f"Unsupported text node type: {text_type}")


def split_nodes_delimiter(old_nodes, delimiter, text_type):

    new_nodes = []
    
    for node in old_nodes:

        if node.text_type == "text":

            if delimiter in node.text:

                parts = node.text.split(delimiter)

                for i, part in enumerate(parts):
                    if i % 2 == 0:
                        new_nodes.append(TextNode(part, "text"))
                    else:
                        new_nodes.append(TextNode(part, text_type))

            else:
                new_nodes.append(node)
        else:
            new_nodes.append(node)
    return new_nodes

def extract_markdown_images(text):
    return re.findall(r"!\[(.*?)\]\((.*?)\)", text)

def extract_markdown_links(text):
    return re.findall(r"\[(.*?)\]\((.*?)\)", text)

def split_nodes_images(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type == TEXT_TYPE_TEXT:
            text = node.text
            while True:
                images = extract_markdown_images(text)
                if not images:
                    break
                description, url = images[0]
                parts = text.split(f"![{description}]({url})", 1)
                if parts[0]:
                    new_nodes.append(TextNode(parts[0], TEXT_TYPE_TEXT))
                new_nodes.append(TextNode(description, TEXT_TYPE_IMAGE, url))
                text = parts[1]
            if text:
                new_nodes.append(TextNode(text, TEXT_TYPE_TEXT))
        else:
            new_nodes.append(node)
    return new_nodes

def split_nodes_links(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type == TEXT_TYPE_TEXT:
            text = node.text
            while True:
                links = extract_markdown_links(text)
                if not links:
                    break
                description, url = links[0]
                parts = text.split(f"[{description}]({url})", 1)
                if parts[0]:
                    new_nodes.append(TextNode(parts[0], TEXT_TYPE_TEXT))
                new_nodes.append(TextNode(description, TEXT_TYPE_LINK, url))
                text = parts[1]
            if text:
                new_nodes.append(TextNode(text, TEXT_TYPE_TEXT))
        else:
            new_nodes.append(node)
    return new_nodes


def text_to_textnodes(text):
    converting_text = [TextNode(text, TEXT_TYPE_TEXT)]
    
    splitting_bold = split_nodes_delimiter(converting_text, "**", TEXT_TYPE_BOLD)

    splitting_italics = split_nodes_delimiter(splitting_bold, "*", TEXT_TYPE_ITALIC)

    splitting_code = split_nodes_delimiter(splitting_italics, "`", TEXT_TYPE_CODE)

    splitting_images = split_nodes_images(splitting_code)

    finished_split = split_nodes_links(splitting_images)

    return finished_split


def markdown_to_blocks(markdown):

    blocks = markdown.strip().split("\n\n")

    return [block.strip() for block in blocks if block.strip()]

block_type_paragraph = "paragraph"
block_type_heading = "heading"
block_type_code = "code"
block_type_quote = "blockquote"
block_type_unordered_list = "unordered list"
block_type_ordered_list = "ordered list"

def block_to_block_types(block):
    for i in range(1, 7):
        if block.startswith("#" * i + " "):
            return f"h{i}"
    
    if block.startswith("```") and block.endswith("```"):
        return block_type_code
    
    lines = block.split("\n")

    if all(line.startswith(">") for line in lines):
        return block_type_quote
    
    if all(line.startswith("* ") or line.startswith("- ") for line in lines):
        return block_type_unordered_list
    
    if all(len(line.split(".")) > 1 and line.split('.')[0].isdigit() and line.split(".")[1].startswith(" ") for line in lines):
        return block_type_ordered_list
    
    else:
        return block_type_paragraph
    
def block_to_heading(block):
    level = 0
    while block[level] == "#":
        level += 1

    text = block[level:].strip()

    return HTMLNode(tag=f"h{level}", value=text)

def block_to_code(block):
    text = block.strip("```").strip()

    code_node = HTMLNode(tag="code", value=text)

    return HTMLNode(tag="pre", value=code_node)

def block_to_ordered_list(block):
    lines = block.split("\n")

    line_items = [item.strip()[item.index(' ') +1:] for item in lines]

    li_nodes = [HTMLNode(tag="li", value=item) for item in line_items]

    return HTMLNode(tag="ol", value=li_nodes)

def block_to_unordered_list(block):
    lines = block.split("\n")

    line_items = [item.strip()[1:].strip() for item in lines if item.startswith("* ")]

    li_nodes = [HTMLNode(tag="li", value=item) for item in line_items]

    return HTMLNode(tag="ul", value=li_nodes)

def block_to_quote(block):
    lines = block.strip().split("\n")

    cleaned_lines = [line.lstrip("> ").rstrip() for line in lines]

    joined_lines = "\n".join(cleaned_lines)

    return HTMLNode(tag="blockquote", value=joined_lines)

def block_to_paragraph(block):
    clean_block = block.strip()
    return HTMLNode(tag="p", value=clean_block)


def markdown_to_html(markdown):
    blocks = markdown_to_blocks(markdown)
    html_nodes = []

    for block in blocks:
        block_type = block_to_block_types(block)

        if block_type == block_type_quote:
            html_nodes.append(block_to_quote(block))

        elif block_type == block_type_code:
            html_nodes.append(block_to_code(block))

        elif block_type == block_type_ordered_list:
            html_nodes.append(block_to_ordered_list(block))
        
        elif block_type == block_type_unordered_list:
            html_nodes.append(block_to_unordered_list(block))

        elif block_type.startswith("h"):
            html_nodes.append(block_to_heading(block))
        
        elif block_type == block_type_paragraph:
            html_nodes.append(block_to_paragraph(block))

    return HTMLNode(tag="div", value=html_nodes)
