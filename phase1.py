from logic_toolkit.wff import WellFormedFormula

input_file = "tests/test1.txt"

with open(input_file, 'r', encoding='utf-8') as f:
    input_lines = f.readlines()

formula = input_lines[1].strip()

try:
    new_instance = WellFormedFormula(formula)
    print('Valid Formula')
    print(new_instance.preorder())
except ValueError:
    print('Invalid Formula')

print("Expected output:", input_lines[4].strip())
print(*(ln.rstrip('\n') for ln in input_lines[5:]), sep='\n')