from chars import *


class Node:
    parent = None

    def __init__(self, name: str, kind: str = "other"):
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
    index = 0
    length = len(content)
    first_bracket = None
    while index < length:
        if content[index] in opening_brackets and first_bracket is None:
            first_bracket = content[index]
        match content[index]:
            case "fn":
                new_node = Node(content[index + 1], "fn")
                root.add_child(new_node)
                index += 1
            case "{":
                new_node = Node(content[index], "block")
                new_node, content = group(new_node, content[index + 1:])
                index = 0
                root.add_child(new_node)
            case "(":
                new_node = Node(content[index], "block")
                new_node, content = group(new_node, content[index + 1:])
                index = 0
                root.add_child(new_node)
            case "[":
                new_node = Node(content[index], "block")
                new_node, content = group(new_node, content[index + 1:])
                index = 0
                root.add_child(new_node)
            case "if":
                new_node = Node("if")
                new_node.add_child(content.pop(index - 1))
                root.add_child(new_node)
            case "}":
                return root, content[index:]
            case ")":
                return root, content[index:]
            case "]":
                return root, content[index:]
            case "eof":
                break
            case _:
                new_node = Node(content[index])
                root.add_child(new_node)
        if len(content) > 0:
            index += 1
        else:
            break

    return root, []


class SyntaxTree:
    def __init__(self, token_list: list[str]):
        token_list.append("eof")
        self.root = Node("root", "root")
        while len(token_list) != 0:
            self.root, token_list = group(self.root, token_list)

    def show(self, node, indent=""):
        print(f"{indent}\"{node.name}\": {node.kind}")
        for item in node.children:
            self.show(item, indent + "  ")
