"""Generate a single-file Python starter for classroom/editor distribution."""
import ast
from pathlib import Path
root = Path(__file__).resolve().parents[1]
tree = ast.parse((root/'python/telemetry.py').read_text())
names = set()
for node in tree.body:
    if isinstance(node, ast.FunctionDef):
        names.add(node.name)
    elif isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name):
                names.add(target.id)
class Rename(ast.NodeTransformer):
    def visit_Name(self, node):
        if node.id in names:
            node.id = 'mt_' + node.id
        return node
    def visit_FunctionDef(self, node):
        if node.name in names:
            node.name = 'mt_' + node.name
        return self.generic_visit(node)
    def visit_Global(self, node):
        node.names = ['mt_'+n if n in names else n for n in node.names]
        return node
tree = Rename().visit(tree)
ast.fix_missing_locations(tree)
library = ast.unparse(tree)
student = '''
# STUDENT PROGRAM: change ID and lesson tag, then add your code below.
from microbit import *
mt_start(1, 'lesson1-v1')
display.show(Image.HAPPY)
while True:
    if button_a.was_pressed():
        display.show('A')
        mt_status('button-a')
    if button_b.was_pressed():
        display.show('B')
        mt_status('button-b')
    mt_poll()
    sleep(20)
'''
out = root/'examples/starter_python.py'
out.write_text('# Single-file classroom starter. Generated from python/telemetry.py.\n'+library+'\n'+student, encoding='utf8')
print(out)
