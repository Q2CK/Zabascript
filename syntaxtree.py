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

    def __eq__(self, other):
        if not isinstance(other, Node):
            return NotImplemented

        return self.name == other.name and self.kind == other.kind

    def add_child(self, child):

        child.parent = self
        child.level = self.level + 1
        self.children.append(child)

        return self

    def get_function(self):

        obj = self

        while obj.parent.parent is not None:
            obj = obj.parent

        return obj

    def get_root(self):

        obj = self

        while obj.parent is not None:
            obj = obj.parent

        return obj


class SyntaxTree:

    errors = []

    def __init__(self, token_list: list[str], output_file):

        self.root = Node("root", "root")

        self.build(token_list, output_file)

    def build(self, token_list, output_file):

        if not all_brackets_closed(token_list):
            self.errors.append("Unclosed brackets found")

        if len(self.errors) == 0:

            self.root, token_list = handle_blocks(self.root, token_list)

            self.root = handle_functions(self.root)

            self.root = self.for_all(self.root, handle_conditionals)
            self.root = self.for_all(self.root, handle_calls)
            self.root = self.for_all(self.root, handle_numeric_unary)
            self.root = self.for_all(self.root, handle_numeric_ambiguous)
            self.root = self.for_all(self.root, handle_numeric_binary)
            self.root = self.for_all(self.root, handle_comparison)
            self.root = self.for_all(self.root, handle_boolean_unary)
            self.root = self.for_all(self.root, handle_boolean_binary)
            self.root = self.for_all(self.root, handle_assignment)
            self.root = self.for_all(self.root, handle_return)
            self.root = self.for_all(self.root, handle_punctuation)

            self.validate()

        if len(self.errors) == 0:

            print("\nSyntax tree:\n")
            self.show(self.root, output_file)
            print("\n")

    def show(self, node: Node, output_file, indent=""):

        output_line = f"{indent}\"{node.name}\": {node.kind}"
        print(output_line)
        output_file.writelines(output_line + "\n")

        for item in node.children:
            self.show(item, output_file, indent + "  ")

    def for_all(self, node: Node, function, data=None):

        if data is None:
            node = function(node)
            for item in node.children:
                self.for_all(item, function)

            return node

        else:
            node, data = function(node, data)
            for item in node.children:
                self.for_all(item, function, data)

            return node, data

    def validate(self):

        self.root, self.errors = self.for_all(self.root, check_errors, self.errors)

        return len(self.errors) == 0


def check_errors(node: Node, errors: list):

    match node.kind:

        case "root":
            for item in node.children:

                if item.kind == "fn":
                    continue

                elif item.kind == "assignment" and item.name == "=":
                    if not (item.children[0].kind == "constant" or (item.children[0].name == "-_"
                            and len(item.children[0].children)) == 1
                            and item.children[0].children[0].kind == "constant"):

                        if len(item.children[0].children) > 0:
                            errors.append(f"Invalid global variable initialisation '{item.children[0].name}"
                                          f"': {item.children[0].kind} - global variables can only be initialised by "
                                          f"constant numeric values")
                        else:
                            errors.append(f"Invalid global variable initialisation '{item.name}':"
                                          f" {item.kind} - global variables can only be initialised by "
                                          f"constant numeric values")

                else:
                    errors.append(f"Unexpected '{item.name}': {item.kind} - root's children must only be function "
                                  f"declarations or global variable assignments")

        case "fn":
            if node.children[0] != Node("(", "block"):
                errors.append(f"Invalid syntax of fn {node.name} declaration - missing arguments block: {'()'}")

            if node.children[1] != Node("{", "block"):
                errors.append(f"Invalid syntax of fn {node.name} declaration - missing body block: {'{}'} ")

        case "return":
            if len(node.children) == 1 and node.children[0].kind not in ["numeric", "boolean", "constant", "other"] \
                    or len(node.children) > 1:
                errors.append(f"Invalid syntax of return '{node.children[0].name}': {node.children[0].kind} from "
                              f"'{node.get_function().name}': fn - must be an arithmetic / boolean expression")

            elif len(node.children) == 0:
                errors.append(f"Invalid syntax of return from '{node.get_function().name}': fn - missing expression")

        case "block":
            if node.name == "(":
                if node.parent.kind == "call":
                    for item in node.children:
                        pass

                elif node.parent.kind == "fn":
                    pass

                else:
                    pass

            elif node.name == "{":
                for idx, item in enumerate(node.children):
                    if item.kind not in ["assignment", "numeric", "call", "loop", "conditional", "return"] and not \
                            (item.kind == "block" and item.name == "{"):
                        errors.append(f"Unexpected standalone '{item.name}': {item.kind} in '{item.get_function().name}"
                                      f"': fn")

                    if item == Node("else", "conditional"):
                        if idx - 1 >= 0 and node.children[idx - 1] != Node("if", "conditional"):
                            errors.append(f"Unexpected standalone 'else': conditional in "
                                          f"'{item.get_function().name}': fn - missing 'if': conditional")

            else:
                pass

        case "loop":
            if len(node.children) != 2 or node.children[0] != Node("(", "block") \
                    or node.children[1] != Node("{", "block"):
                errors.append(f"Invalid syntax of 'while': loop in '{node.get_function().name}': fn - "
                              f"'while': loop requires only a condition block and body block")
            else:
                if len(node.children[0].children) != 1 or not \
                        (node.children[0].children[0].kind in ["boolean", "comparison"]
                         or node.children[0].children[0] in [Node("True", "comparison"), Node("False", "comparison")]):
                    errors.append(f"Invalid syntax of 'while': loop in '{node.get_function().name}': fn - "
                                  f"'while': expected boolean expression in condition block")

        case "conditional":
            if node.name in ["if", "else"]:
                if len(node.children) != 2 or node.children[0] != Node("(", "block") \
                        or node.children[1] != Node("{", "block"):
                    errors.append(f"Invalid syntax of 'if' conditional in '{node.get_function().name}': fn - "
                                  f"'{node.name}': conditional requires only a condition block and body block")
                else:
                    if len(node.children[0].children) != 1 or not \
                            (node.children[0].children[0].kind in ["boolean", "comparison"]
                             or node.children[0].children[0] in [Node("True", "comparison"),
                                                                 Node("False", "comparison")]):
                        errors.append(f"Invalid syntax of if in '{node.get_function().name}': fn - "
                                      f"'{node.name}': conditional expected boolean expression in condition block")

        case "numeric":
            for item in node.children:
                if item.kind not in ["numeric", "other", "call", "constant"] and item != Node("(", "block"):
                    errors.append(f"Invalid algebraic expression in '{node.get_function().name}': fn - "
                                  f"'{node.name}': {node.kind} - unexpected '{item.name}': {item.kind}")

        case "boolean":
            for item in node.children:
                if item.kind not in ["comparison", "boolean", "call"] and item != Node("(", "block"):
                    errors.append(f"Invalid boolean expression in '{node.get_function().name}': fn - "
                                  f"'{node.name}': {node.kind} - unexpected '{item.name}': {item.kind}")

        case "comparison":
            for item in node.children:
                if item.kind in ["numeric", "constant", "other", "call"]:
                    pass
                else:
                    errors.append(f"Invalid comparison in '{node.get_function().name}': fn - "
                                  f"'{node.name}': {node.kind} - unexpected '{item.name}': {item.kind}")

        case "quote":
            pass

    return node, errors


def is_constant(item: str):

    for letter in item:
        if letter not in digits:
            return False

    return True


def handle_blocks(root: Node, content: list):

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
            case "while":
                new_node = Node(content[index], "loop")
            case "if" | "else":
                new_node = Node(content[index], "conditional")
            case '++' | '+' | '-' | '*' | '/' | '%' | '&' | '|' | '^' | '~':
                new_node = Node(content[index], "numeric")
            case "and" | "or" | "not":
                new_node = Node(content[index], "boolean")
            case "!=" | "==" | "<" | ">" | "<=" | ">=" | "True" | "False":
                new_node = Node(content[index], "comparison")
            case "\"" | "'":
                new_node = Node(content[index], "quote")
            case "," | "." | ";" | ":":
                new_node = Node(content[index], "punctuation")
            case "=" | '--' | '+=' | '-=' | '*=' | '/=' | '%=':
                new_node = Node(content[index], "assignment")
            case "eof":
                break
            case _:
                if is_constant(content[index]):
                    new_node = Node(content[index], "constant")
                else:
                    new_node = Node(content[index])

        root.add_child(new_node)

        index += 1

    return root, []


def handle_functions(node: Node):

    index = 0

    length = len(node.children) - 1
    content = node.children

    while index < length:
        if node.name == "root" and node.kind == "root" and content[index].kind == "fn":

            node.data.append(content[index].name)

            content[index].add_child(content.pop(index + 1))
            content[index].add_child(content.pop(index + 1))

        index += 1
        length = len(content) - 1

    return node


def handle_conditionals(node: Node):

    index = 0

    length = len(node.children) - 1
    content = node.children

    while index < length:
        if content[index].kind in ["conditional", "loop"]:

            content[index].add_child(content.pop(index + 1))
            content[index].add_child(content.pop(index + 1))

            node.data.append((content[index].name, "function"))

        index += 1
        length = len(content) - 1

    return node


def handle_calls(node: Node):

    index = 0

    length = len(node.children) - 1
    content = node.children

    while index < length:

        if content[index].kind == "other" and content[index].name in node.get_root().data:

            content[index].add_child(content.pop(index + 1))
            content[index].kind = "call"

        index += 1
        length = len(content) - 1

    return node


def handle_numeric_unary(node: Node):

    index = 0

    length = len(node.children) - 1
    content = node.children

    while index < length:

        if content[index].kind == "other" and content[index + 1].kind == "numeric" \
                and content[index + 1].name in ["++", "--"]:

            content[index + 1].add_child(content.pop(index))
            index -= 1

            content[index + 1].name = "_" + content[index + 1].name

        elif content[index + 1].kind == "other" and content[index].kind == "numeric" \
                and content[index].name in ["++", "--"]:

            content[index].add_child(content.pop(index + 1))

            content[index].name = content[index].name + "_"

        index += 1
        length = len(content) - 1

    return node


def handle_numeric_ambiguous(node: Node):

    index = 0

    length = len(node.children) - 1
    content = node.children

    while index < length:

        if content[index].name in ["-", "*", "&"] and content[index].kind == "numeric":

            if index > 0 and (content[index - 1].kind in ["numeric", "other", "constant"]
                    or (content[index - 1].kind == "block" and content[index - 1].name == "(")):

                content[index].add_child(content.pop(index + 1))
                content[index].add_child(content.pop(index - 1))
                index -= 1

            elif index == 0 or (index > 0 and (content[index - 1].kind not in ["numeric", "other", "constant"]
                    or content[index - 1].kind == "block" and content[index - 1].name == "(")):

                content[index].add_child(content.pop(index + 1))
                content[index].name = content[index].name + "_"

        index += 1
        length = len(content) - 1

    return node


def handle_numeric_binary(node: Node):

    index = 0

    length = len(node.children) - 1
    content = node.children

    while index < length:
        if index > 0 and content[index].name in ["+", "/", "%", "|", "^", "<<", ">>"] \
                and content[index].kind == "numeric":

            content[index].add_child(content.pop(index + 1))
            content[index].add_child(content.pop(index - 1))
            index -= 1

        index += 1
        length = len(content) - 1

    return node


def handle_comparison(node: Node):

    index = 0

    length = len(node.children) - 1
    content = node.children

    while index < length:
        if content[index].kind == "comparison":

            content[index].add_child(content.pop(index + 1))
            content[index].add_child(content.pop(index - 1))

        index += 1
        length = len(content) - 1

    return node


def handle_boolean_unary(node: Node):

    index = 0

    length = len(node.children) - 1
    content = node.children

    while index < length:

        if content[index].name == "not" and content[index].kind == "numeric":

            content[index].add_child(content.pop(index + 1))

        index += 1
        length = len(content) - 1

    return node


def handle_boolean_binary(node: Node):

    index = 0

    length = len(node.children) - 1
    content = node.children

    while index < length:
        if index > 0 and content[index].name in ["and", "or"] and content[index].kind == "boolean":

            content[index].add_child(content.pop(index + 1))
            content[index].add_child(content.pop(index - 1))
            index -= 1

        index += 1
        length = len(content) - 1

    return node


def handle_assignment(node: Node):

    index = 0

    length = len(node.children) - 1
    content = node.children

    while index < length:
        if index > 0 and content[index].kind == "assignment":

            content[index].add_child(content.pop(index + 1))
            content[index].add_child(content.pop(index - 1))
            index -= 1

        index += 1
        length = len(content) - 1

    return node


def handle_return(node: Node):

    index = 0

    length = len(node.children) - 1
    content = node.children

    while index < length:
        if content[index].kind == "return":

            content[index].add_child(content.pop(index + 1))

        index += 1
        length = len(content) - 1

    return node


def handle_punctuation(node: Node):

    return node


def all_brackets_closed(token_list: list[str]):

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
