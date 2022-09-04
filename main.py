import os

from syntaxtree import *
from separate import *

input_file_name = ""
input_string = ""

while True:
    try:
        input_file_name = input("Żabascript file name: ")
        input_string: str = open(os.path.abspath(input_file_name)).read()
    except FileNotFoundError:
        print(f"File {input_file_name} not found")
        continue
    else:
        break

output_file = open("out_" + input_file_name.split(".")[0] + ".tree", "w")

token_list, line_number_list = separate(input_string)
ast = SyntaxTree(token_list)

ast.validate()

for error in ast.errors:
    print(error)

print("\nAbstract syntax tree:\n")
ast.show(ast.root, output_file)

input("\nPress enter to quit...")


