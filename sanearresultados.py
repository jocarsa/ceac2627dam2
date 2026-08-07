#!/usr/bin/env python3

import re

input_file = "Resultados de aprendizaje y criterios de evaluación.md"
output_file = "Resultados de aprendizaje y criterios de evaluación-list.md"

with open(input_file, "r", encoding="utf-8", newline="") as fin, \
     open(output_file, "w", encoding="utf-8", newline="") as fout:

    for line in fin:
        # Separate line ending
        if line.endswith("\r\n"):
            ending = "\r\n"
            text = line[:-2]
        elif line.endswith("\n"):
            ending = "\n"
            text = line[:-1]
        else:
            ending = ""
            text = line

        # Keep original indentation (tabs/spaces)
        m = re.match(r"^([ \t]*)(.*)$", text)
        indent, content = m.groups()

        fout.write(f"{indent}- {content}{ending}")

print("Done.")
