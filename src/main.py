from textnode import TextNode, TextType

def main():
    text_node = TextNode("This is some anchor text", TextType.LINK, "https://www.google.com")
    print(text_node)

main()