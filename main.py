from syntaxtree import *
from separate import *

input_file_name = ""
input_string = ""

while True:
    try:
        input_file_name = input("Żabascript file name: ")
        input_string: str = open(input_file_name).read()
    except FileNotFoundError:
        print("File not found")
        continue
    else:
        break

output_file = open("out_" + input_file_name.split(".")[0] + ".tree", "w")

token_list = separate(input_string).split()
ast = SyntaxTree(token_list)

print("\nAbstract syntax tree:\n")
ast.show(ast.root, output_file)

input()


