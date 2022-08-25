import json
from syntaxtree import *
from separate import separate

keywords: list[str] = json.loads(open("torch.json").read()).keys()
keywords = sorted(keywords, key=len, reverse=True)

torch: str = open("test.tr").read()
output = open("output.txt", "w")

ast = SyntaxTree()

token_list = separate(torch).split()
ast.parse(token_list)

ast.show(ast.root)

print(separate(torch))
