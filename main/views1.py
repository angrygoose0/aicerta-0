import re

sec = "(a)(i)"

match = re.search(r"\((.*?)\)\((.*?)\)", sec)

primary = match.group(1)
secondary = match.group(2)

print(primary)
print(secondary)