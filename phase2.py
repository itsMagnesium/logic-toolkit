from logic_toolkit.cnf import CNF

input_file = "tests/test21.txt"

with open(input_file, 'r', encoding='utf-8') as f:
    input_lines = f.readlines()

cnf_str = input_lines[1].strip()

cnf = CNF(cnf_str)
print(cnf)

print("Expected output:", input_lines[4].strip())