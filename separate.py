from chars import *


def separate(input_string: str):

    input_string += " eof"

    i = 1
    line = 0

    line_number_list = []
    beginning = 0

    while i < len(input_string):

        if input_string[i] == "\n":
            line += 1
            tokens_in_line = len(input_string[beginning:i].split())
            beginning = i + 1
            for n in range(0, tokens_in_line):
                line_number_list.append(line)

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

    return input_string.split(), line_number_list
