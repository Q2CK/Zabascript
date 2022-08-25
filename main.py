from syntaxtree import *
from separate import *
from chars import *

keywords = sorted(keywords, key=len, reverse=True)

torch: str = open("test.tr").read()
output = open("output.txt", "w")

token_list = separate(torch).split()
ast = SyntaxTree(token_list)
ast.show(ast.root)

