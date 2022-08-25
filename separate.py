from chars import *


def separate(input_string: str):
    i: int = 1
    while i < len(input_string) - 1:
        if input_string[i] in absolute_separators:
            input_string = input_string[:i] + " " + input_string[i:]
            i += 1
            input_string = input_string[:i + 1] + " " + input_string[i + 1:]
            i += 1
        if input_string[i] in possible_separators and input_string[i - 1] not in possible_separators:
            input_string = input_string[:i] + " " + input_string[i:]
            i += 1
        if input_string[i] in possible_separators and input_string[i + 1] not in possible_separators:
            input_string = input_string[:i + 1] + " " + input_string[i + 1:]
            i += 1
        i += 1

    return " ".join(input_string.split())
