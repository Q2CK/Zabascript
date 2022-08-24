class Node:
    parent = None

    def __init__(self, kind, name="default"):
        self.kind = kind
        self.name = name
        self.children = []

    def add_child(self, child):
        self.children.append(child)
        child.parent = self
        return self


class SyntaxTree:
    def __init__(self):
        self.root = Node("root", "root")

    def parse(self, token_list):
        for index in range(0, len(token_list) - 1):
            if token_list[index] == "fn":
                new_node = Node("fn", token_list[index])

                # CREATE FUNCTIONS TO GENERATE BLOCKS

                args = None
                code_block = None

                new_node.children.append(args)
                new_node.children.append(code_block)

                self.root.add_child(new_node)
