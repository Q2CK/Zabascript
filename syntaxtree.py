from chars import *


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

        index += 1

    return root, []


def handle_functions(node):

    index = 0
    length = len(node.children) - 1
    content = node.children

    while index < length:
        if node.name == "root" and node.kind == "root" and content[index].kind == "fn":
            content[index].children.append(content.pop(index + 1))
            content[index].children.append(content.pop(index + 1))

        index += 1
        length = len(content) - 1

    return node


def handle_conditionals(node):

    index = 0
    length = len(node.children) - 1
    content = node.children

    while index < length:
        if content[index].kind in ["conditional", "loop"]:

            content[index].children.append(content.pop(index + 1))
            content[index].children.append(content.pop(index + 1))

            node.data.append((content[index].name, "function"))

        index += 1
        length = len(content) - 1

    return node


function_names = []


def handle_calls(node):

    if node.name == "root" and node.kind == "root":
        for item in node.children:
            if item.kind == "fn":
                function_names.append(item.name)

    index = 0
    length = len(node.children) - 1
    content = node.children

    while index < length:
        if content[index].kind == "other" and content[index].name in function_names:

            content[index].children.append(content.pop(index + 1))

        index += 1
        length = len(content) - 1

    return node


def handle_numeric_binary(node):

    index = 0
    length = len(node.children) - 1
    content = node.children

    while index < length:
        if index > 0 and content[index].name in ["+", "/", "%", "&", "|", "^"] and content[index].kind == "numeric":

            content[index].children.append(content.pop(index + 1))
            content[index].children.append(content.pop(index - 1))
            index -= 1

        elif content[index].name in ["-", "*"] and content[index].kind == "numeric":

            if index > 0 and (content[index - 1].kind in ["numeric", "other"] or
                    (content[index - 1].kind == "block" and content[index - 1].name == "(")):

                content[index].children.append(content.pop(index + 1))
                content[index].children.append(content.pop(index - 1))
                index -= 1

            elif index > 0 and not (index > 0 and (content[index - 1].kind in ["numeric", "other"] or
                    (content[index - 1].kind == "block" and content[index - 1].name == "("))):

                content[index].children.append(Node("0"))
                content[index].children.append(content.pop(index + 1))

        index += 1
        length = len(content) - 1

    return node


def all_brackets_closed(token_list):

    curly_counter = 0
    round_counter = 0
    square_counter = 0

    for token in token_list:
        match token:
            case "{":
                curly_counter += 1
            case "}":
                curly_counter -= 1
            case "(":
                round_counter += 1
            case ")":
                round_counter -= 1
            case "[":
                square_counter += 1
            case "]":
                square_counter -= 1

    return curly_counter == 0 and round_counter == 0 and square_counter == 0


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


class SyntaxTree:

    errors = []

    def __init__(self, token_list: list[str]):

        token_list.append("eof")

        if not all_brackets_closed(token_list):
            self.errors.append("Unclosed bracket found")

        self.root, token_list = handle_blocks(Node("root", "root"), token_list)

        self.root = handle_functions(self.root)

        self.root = self.for_all(self.root, handle_conditionals)
        self.root = self.for_all(self.root, handle_calls)
        self.root = self.for_all(self.root, handle_numeric_binary)

    def show(self, node, output_file, indent=""):

        output_line = f"{indent}\"{node.name}\": {node.kind}"
        print(output_line)
        output_file.writelines(output_line + "\n")

        for item in node.children:
            self.show(item, output_file, indent + "  ")

    def for_all(self, node, function):

        display = ""
        display += f"{node.name}({node.kind}): "

        node = function(node)

        for item in node.children:
            self.for_all(item, function)
            display += f"{item.name}({item.kind}), "

        return node
