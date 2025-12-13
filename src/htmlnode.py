class HTMLNode():
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError()

    def props_to_html(self):
        if self.props == None or len(self.props) == 0:
            return ""
        result_string = ""
        for key, value in self.props.items():
            result_string += f" {key}=\"{value}\""
        return result_string

    def __repr__(self):
        return f"tag: {self.tag}\nvalue: {self.value}\nchildren: {self.children}\nprops: {self.props}"
    
class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag, value, None, props)

    def to_html(self):
        if not self.value:
            raise ValueError("All leaf nodes must have a value")
        if not self.tag:
            return f"{self.value}"
        if not self.props:
            return f"<{self.tag}>{self.value}</{self.tag}>"
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"
    
class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag, None, children, props)

    def to_html(self):
        result_string = f"<{self.tag}>"
        if not self.tag:
            raise ValueError("All parent nodes must have a tag")
        if not self.children:
            raise ValueError("All parent nodes must have children")
        for child in self.children:
            result_string += f"{child.to_html()}"
        return result_string + f"</{self.tag}>"