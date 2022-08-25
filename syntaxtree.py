from chars import *


class Node:
    parent = None

    def __init__(self, kind: str, name: str = "default"):
        self.level = 0
        self.kind = kind
        self.name = name
        self.children = []

    def add_child(self, child):
        self.children.append(child)
        child.parent = self
        child.level = self.level + 1
        return self


def block(kind: str, content: list[str]):

    counter: int = 0

    inserted_tokens = []


class SyntaxTree:
    def __init__(self):
        self.root = Node("root", "root")

    def parse(self, token_list: list[str]):
        index: int = 0
        while index < len(token_list) - 1:
            if token_list[index] == "fn":
                new_node = Node("fn", token_list[index + 1])
                self.root.add_child(new_node)
            index += 1

    def show(self, node, indent=""):
        print(f"{indent}{node.name}: {node.kind}")
        for item in node.children:
            self.show(item, indent + "  ")

