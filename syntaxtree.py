from chars import *


class Node:
    parent = None

    def __init__(self, name: str, kind: str = "other", data=None):
        if data is None:
            data = []
        self.data = data
        self.level = 0
        self.kind = kind
        self.name = name
        self.children = []

    def add_child(self, child):
        self.children.append(child)
        child.parent = self
        child.level = self.level + 1
        return self


def handle_blocks(root, content: list):
    index = 0
    length = len(content)
    first_bracket = None

    while index < length:

        if content[index] in opening_brackets and first_bracket is None:
            first_bracket = content[index]

        match content[index]:
            case "fn":
                new_node = Node(content[index + 1], "fn")
                index += 1
            case "return":
                new_node = Node(content[index], "return")
            case "{" | "(" | "[":
                new_node = Node(content[index], "block")
                new_node, content = handle_blocks(new_node, content[index + 1:])
                index = 0
            case "}" | ")" | "]":
                return root, content[index:]
            case "match":
                new_node = Node(content[index], "match")
            case "while":
                new_node = Node(content[index], "loop")
            case "if" | "else":
                new_node = Node(content[index], "conditional")
            case '++' | '--' | '+=' | '-=' | '*=' | '/=' | '%=' | '+' | '-' | '*' | '/' | '%' | '&' | '|' | '^' | '~':
                new_node = Node(content[index], "numeric")
            case "and" | "or" | "not":
                new_node = Node(content[index], "boolean")
            case "!=" | "==" | "<" | ">" | "<=" | ">=":
                new_node = Node(content[index], "comparison")
            case "\"" | "'":
                new_node = Node(content[index], "quote")
            case "," | "." | ";" | ":":
                new_node = Node(content[index], "punctuation")
            case "=":
                new_node = Node(content[index], "assignment")
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


def handle_functions(node):
    index = 0
    while index < len(node.children) - 1:

        if node.name == "root" and node.kind == "root" and node.children[index].kind == "fn":

            node.children[index].children.append(node.children.pop(index + 1))
            node.children[index].children.append(node.children.pop(index + 1))

            node.data.append((node.children[index].name, "function"))

        elif node.name == "root" and node.kind == "root" and node.children[index].kind != "fn":
            print("Not a function")

        index += 1

    return node

def handle_operators(node):
    pass


class SyntaxTree:
    def __init__(self, token_list: list[str]):
        token_list.append("eof")
        self.root, token_list = handle_blocks(Node("root", "root"), token_list)
        self.root = handle_functions(self.root)

    def show(self, node, indent=""):
        print(f"{indent}\"{node.name}\": {node.kind}")
        for item in node.children:
            self.show(item, indent + "│ ")

    def for_all(self, node, function):
        display = ""
        display += f"{node.name}({node.kind}): "

        node = function(node)

        for item in node.children:
            self.for_all(item, function)
            display += f"{item.name}({item.kind}), "
