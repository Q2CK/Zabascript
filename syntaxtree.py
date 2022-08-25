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


def block(content: list):
    content.append("eof")
    if content[0] in opening_brackets:
        first_bracket = content.pop(0)
        return_block = Node("block", first_bracket)
        index = 0
        while index < len(content):
            if content[index] in opening_brackets:
                content, new_block = block(content[index:])
                return_block.add_child(new_block)
            elif content[index] == closing_brackets[opening_brackets.index(first_bracket)]:
                return content[index + 1:], return_block
            else:
                return_block.add_child(Node(content[index]))
            index += 1
        print("Block ending not found")
        return content[index + 1:], None
    else:
        print("Block not found")
        return content, None


class SyntaxTree:
    def __init__(self):
        self.root = Node("root", "root")

    def build_ast(self, token_list: list[str]):
        index: int = 0
        while index < len(token_list) - 1:
            if token_list[index] == "fn":
                new_node = Node(token_list.pop(index), token_list.pop(index))

                token_list, new_block = block(token_list)
                if new_block is not None:
                    new_node.add_child(new_block)
                token_list, new_block = block(token_list)
                if new_block is not None:
                    new_node.add_child(new_block)

                self.root.add_child(new_node)
            index += 1

    def show(self, node, indent=""):
        print(f"{indent}{node.name}: {node.kind}")
        for item in node.children:
            self.show(item, indent + "  ")
