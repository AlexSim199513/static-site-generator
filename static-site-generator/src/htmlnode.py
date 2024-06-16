class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props
    def to_html(self):
        raise NotImplementedError
    
    def props_to_html(self):
        string = " "
        for key, value in self.props.items():
            string += f"{key}={value} "
        return string 
    
    def __eq__(self, other):
        if isinstance(other, HTMLNode):
            tags_equal = self.tag == other.tag
            values_equal = self.value == other.value
            if not tags_equal:
                print(f"Tags do not match: {self.tag} != {other.tag}")
            if not values_equal:
                print(f"Values do not match: {self.value} != {other.value}")
            return tags_equal and values_equal
        return False
    
    def __repr__(self):
        return f"HTMLNode(tag={self.tag}, value={self.value})"
    
class LeafNode(HTMLNode):
    def __init__(self, value, tag=None, props=None):
        if value is None:
            raise ValueError("LeafNode requires a value")
        super().__init__(tag=tag, value=value, children=None, props=props)
        self.children = None

    def to_html(self):
        if self.tag == None:
            return self.value
        else:
            props_str = self.props_to_html() if self.props else ""
            return f"<{self.tag}{props_str}>{self.value}</{self.tag}>"


class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        if not tag:
            raise ValueError("ParentNode must have a tag")
        
        if not children:
            raise ValueError("ParentNode must have children")
        
        super().__init__(tag=tag, value=None, children=children, props=props)

    def to_html(self):
        if not self.tag:
            raise ValueError("ParentNode must have a tag")
        
        if not self.children:
            raise ValueError("ParentNode must have children")
        
        html_string = f"<{self.tag}>"

        for child in self.children:
            html_string += child.to_html()

        html_string += f"</{self.tag}>"
         
        return html_string