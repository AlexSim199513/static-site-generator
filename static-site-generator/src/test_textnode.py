import unittest

from textnode import TextNode


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", "bold")
        node2 = TextNode("This is a text node", "bold")
        self.assertEqual(node, node2)
    def test_None(self):
        node = TextNode("test", "italic", None)
        node2 = TextNode("test", "italic", None)
        node3 = TextNode("test", "italic")
        self.assertEqual(node, node2)
        self.assertEqual(node, node3)
    def test_text_type(self):
        node = TextNode("testing", "bold")
        node2 = TextNode("testing", "italics")
        self.assertNotEqual(node, node2)
    def test_empty_text(self):
        node1 = TextNode("", "italic")
        node2 = TextNode("", "italic")
        self.assertEqual(node1, node2)


if __name__ == "__main__":
    unittest.main()