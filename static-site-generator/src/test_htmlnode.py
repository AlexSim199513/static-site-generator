import unittest

from textnode import TextNode
from htmlnode import HTMLNode, LeafNode, ParentNode
from conversion import (
    text_node_to_html_node, 
    split_nodes_delimiter, 
    TEXT_TYPE_BOLD,
    TEXT_TYPE_CODE,
    TEXT_TYPE_IMAGE,
    TEXT_TYPE_ITALIC,
    TEXT_TYPE_LINK,
    TEXT_TYPE_TEXT,
    extract_markdown_links,
    extract_markdown_images,
    split_nodes_images,
    split_nodes_links,
    text_to_textnodes,
    markdown_to_blocks,
    block_to_heading,
    block_to_code,
    block_to_ordered_list,
    block_to_unordered_list,
    block_to_quote,
    block_to_paragraph
)


class TestHTMLNode(unittest.TestCase):
    def test_props_to_html(self):
        node = HTMLNode("img", "boot.png", None, {"href": "https://www.google.com", "target": "_blank"})
        expected_string = " href=https://www.google.com target=_blank "
        self.assertEqual(node.props_to_html(), expected_string)

    def test_props2_to_html(self):
        node = HTMLNode("img", "boot.png", None, {"href": "https://www.Boot.dev"})
        expected_string = " href=https://www.Boot.dev "
        self.assertEqual(node.props_to_html(), expected_string)

    def test_LeafNode_to_html(self):
        node = LeafNode("This is a node", "h1")
        expected_string = "<h1>This is a node</h1>"
        self.assertEqual(node.to_html(), expected_string)

    def test_no_value(self):
        with self.assertRaises(ValueError) as context:
            node = LeafNode(None, "p")
        self.assertEqual(str(context.exception), "LeafNode requires a value")

    def test_parent_to_html(self):

        node = ParentNode(
            "p", 
            [
            LeafNode("Bold text", "b"),
            LeafNode("Normal text", None),
            LeafNode("italic text", "i"),
            LeafNode("Normal text", None),
        ])
        expected_string = "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>"
        self.assertEqual(node.to_html(), expected_string)

    def test_no_children(self):
        with self.assertRaises(ValueError) as context:
            node = ParentNode("h1", None, None)
        self.assertEqual(str(context.exception), "ParentNode must have children")

    def test_empty_children_list(self):
        with self.assertRaises(ValueError) as context:
            node = ParentNode("h1", [])
        self.assertEqual(str(context.exception), "ParentNode must have children")

    def test_nested_parents(self):
        nested_node = ParentNode(
            "div",
            [
                ParentNode(
                    "span",
                    [
                        LeafNode("Nested Bold", "b")
                    ]
                )
            ]
        )
        expected_string = "<div><span><b>Nested Bold</b></span></div>"
        self.assertEqual(nested_node.to_html(), expected_string)

    def test_parent_without_tag(self):
        with self.assertRaises(ValueError) as context:
            node = ParentNode(None, [LeafNode("normal text", "p")])
        self.assertEqual(str(context.exception), "ParentNode must have a tag")

    
    def test_delimiter(self):
        node = TextNode("this is text with **bold** and more text", TEXT_TYPE_TEXT)
        result = split_nodes_delimiter([node], "**", TEXT_TYPE_BOLD)

        expected = [
            TextNode("this is text with ", TEXT_TYPE_TEXT),
            TextNode("bold", TEXT_TYPE_BOLD),
            TextNode(" and more text", TEXT_TYPE_TEXT)
        ]

        self.assertEqual(result, expected, f"Expected {expected}, but got {result}")

    def test_delimiter_without_delimiter(self):
        node = TextNode("this is text with **bold** and more text", TEXT_TYPE_TEXT)
        result = split_nodes_delimiter([node], "`", TEXT_TYPE_CODE)

        expected = [node]

        self.assertEqual(result, expected, f"Expected {expected}, but got {result}")

    def test_delimiter_with_non_type_text(self):
        node = TextNode("**bold**", TEXT_TYPE_BOLD)
        result = split_nodes_delimiter([node], "**", TEXT_TYPE_BOLD)

        expected = [node]

        self.assertEqual(result, expected, f"Expected {expected}, but got {result}")
    
    def test_extract_markdown_images(self):
        text = "This is text with an ![image](https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png) and ![another](https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/dfsdkjfd.png)"
        result =  extract_markdown_images(text)

        expected = [("image", "https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png"), ("another", "https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/dfsdkjfd.png")]

        self.assertEqual(result, expected, f"Expected: {expected}, but got {result}")

    def test_extract_markdown_links(self):
        text = "This is text with a [link](https://www.example.com) and [another](https://www.example.com/another)"
        result = extract_markdown_links(text)

        expected = [("link", "https://www.example.com"), ("another", "https://www.example.com/another")]

        self.assertEqual(result, expected, f"Expected: {expected}, but got {result}")

    def _test_split_links(self):
        nodes = [TextNode(
            "Here is a [link_one](https://example.com/one) and another [link_two](https://example.com/two).",
            TEXT_TYPE_TEXT
        )]
        
        result = split_nodes_links(nodes)

        expected = [TextNode("Here is a ", "text", "None"), TextNode("link_one", "link", "https://example.com/one"), TextNode(" and another ", "text", "None"), TextNode("link_two", "link", "https://example.com/two"), TextNode(".", "text", "None")]

        self.assertEqual(result, expected)

    def test_split_images(self):
        nodes = [TextNode(
            "This is text with an ![image](https://example.com/image1.png) and another ![second image](https://example.com/image2.png)",
            TEXT_TYPE_TEXT
        )]

        result = split_nodes_images(nodes)

        expected = [
            TextNode("This is text with an ", TEXT_TYPE_TEXT),
            TextNode("image", TEXT_TYPE_IMAGE, "https://example.com/image1.png"),
            TextNode(" and another ", TEXT_TYPE_TEXT),
            TextNode("second image", TEXT_TYPE_IMAGE, "https://example.com/image2.png")
        ]

        self.assertEqual(result, expected) 

    def test_block_to_code(self):
        # Example code block
        code_block = "```\nprint('Hello, World!')\n```"

        # Testing the block_to_code function
        result = block_to_code(code_block)

        # Create expected result nodes for comparison
        expected_inner_node = HTMLNode(tag="code", value="print('Hello, World!')")
        expected_outer_node = HTMLNode(tag="pre", value=expected_inner_node)

        # Assertion to check correctness
        self.assertEqual(result, expected_outer_node)

    def test_markdown_to_blocks(self):
        markdown = """This is a **bolded** paragraph

This is another paragraph with *italic* text and `code` here
This is the same paragraph on a new line

* This is a list
* with items"""
            
        result = markdown_to_blocks(markdown)

        expected = ["This is a **bolded** paragraph", "This is another paragraph with *italic* text and `code` here\nThis is the same paragraph on a new line", "* This is a list\n* with items"]

        self.assertEqual(expected, result), f"Expected: {expected}, but got {result}"

    def test_block_to_heading(self):
        heading1 = "# Heading 1"
        heading2 = "## Heading 2"
        heading3 = "### Heading 3"

        # Testing the block_to_heading function
        node1 = block_to_heading(heading1)
        node2 = block_to_heading(heading2)
        node3 = block_to_heading(heading3)

        # Assertions to check correctness
        self.assertEqual(node1.tag, "h1")
        self.assertEqual(node1.value, "Heading 1")
        
        self.assertEqual(node2.tag, "h2")
        self.assertEqual(node2.value, "Heading 2")

        self.assertEqual(node3.tag, "h3")
        self.assertEqual(node3.value, "Heading 3")

    def test_block_to_code(self):
        code_block = "```\nprint('Hello, World!')\n```"

        result = block_to_code(code_block)

        expected_inner_node = HTMLNode(tag="code", value="print('Hello, World!')")
        expected_outer_node = HTMLNode(tag="pre", value=expected_inner_node)

        self.assertEqual(result, expected_outer_node)

    def test_block_to_ordered_list(self):
        # Example ordered list block
        ol_block = "1. First item\n2. Second item\n3. Third item"

        # Testing the block_to_ordered_list function
        result = block_to_ordered_list(ol_block)
        
        # Create expected result nodes for comparison
        expected_li_nodes = [
            HTMLNode(tag="li", value="First item"),
            HTMLNode(tag="li", value="Second item"),
            HTMLNode(tag="li", value="Third item")
        ]
        expected_ol_node = HTMLNode(tag="ol", value=expected_li_nodes)

        self.assertEqual(result, expected_ol_node)

    def test_block_to_unordered_list(self):
        ul_block = "* First item\n* Second item\n* Third item"
        
        result = block_to_unordered_list(ul_block)
        
        expected_li_nodes = [
            HTMLNode(tag="li", value="First item"),
            HTMLNode(tag="li", value="Second item"),
            HTMLNode(tag="li", value="Third item")
        ]

        expected_ul_node = HTMLNode(tag="ul", value=expected_li_nodes)

        self.assertEqual(result, expected_ul_node)

    def test_block_to_blockquote(self):
        blockquote_block = "> This is a quote.\n> It spans multiple lines."
        
        result = block_to_quote(blockquote_block)

        expected_text = "This is a quote.\nIt spans multiple lines."
        expected_blockquote_node = HTMLNode(tag="blockquote", value=expected_text)
        
        self.assertEqual(result, expected_blockquote_node)

    def test_block_to_paragraph(self):
        paragraph_block = "   This is a paragraph.   "
        
        result = block_to_paragraph(paragraph_block)

        expected_paragraph_node = HTMLNode(tag="p", value="This is a paragraph.")
        
        # Debugging Output
        print(f"Result: {repr(result)}")
        print(f"Expected: {repr(expected_paragraph_node)}")
        
        self.assertEqual(result, expected_paragraph_node)

if __name__ == "__main__":
    unittest.main()