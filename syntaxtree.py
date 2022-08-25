from chars import *


class Node:
    parent = None

    def __init__(self, kind: str, name: str = "other"):
        self.level = 0
        self.kind = kind
        self.name = name
        self.children = []

    def add_child(self, child):
        self.children.append(child)
        child.parent = self
        child.level = self.level + 1
        return self


def group(root, content: list):
    content.append("eof")
    index = 0
    length = len(content)
    print(content)
    while index < length and length > 1:
        new_node = Node("None")
        if content[index] == "fn":
            new_node = Node(content[index], content[index + 1])
            index += 2
        if content[index] == "eof":
            new_node = Node(content[index])
            index += 2
        root.add_child(new_node)
        index += 1

    return root


class SyntaxTree:
    def __init__(self, token_list: list[str]):
        self.root = Node("root", "root")
        self.root = group(self.root, token_list)

    def show(self, node, indent=""):
        print(f"{indent}{node.name}: {node.kind}")
        for item in node.children:
            self.show(item, indent + "  ")
