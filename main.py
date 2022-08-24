import json
from separate import separate

keywords: list[str] = json.loads(open("torch.json").read()).keys()
keywords = sorted(keywords, key=len, reverse=True)

torch = open("test.tr").read()
output = open("output.txt", "w")

print(separate(torch))
