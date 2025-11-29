from lark import Lark, Transformer, v_args

GRAMMAR = r"""
start: (constant | dict)*

constant: "(" "define" NAME value ")"

dict: "begin" (assignment ";")* "end"

assignment: NAME ":=" value

value: number | string | dict | constant_usage
constant_usage: "[" NAME "]"

number: SIGNED_INT
string: ESCAPED_STRING
NAME: /[a-zA-Z][a-zA-Z0-9_]*/

%import common.SIGNED_INT
%import common.ESCAPED_STRING
%import common.WS
%ignore WS
COMMENT: /\(comment[^)]*\)/
%ignore COMMENT
"""

def make_parser():
    return Lark(GRAMMAR, parser="lalr")

# ---------------------------------------------------------
@v_args(inline=True)
class ConfigTransformer(Transformer):
    """Трансформер для конфигурационного языка"""
    def __init__(self):
        self.constants = {}

    # Constants
    def constant(self, name, value):
        self.constants[name.value] = value
        return None

    # Dicts
    def dict(self, *assignments):
        assignments = [a for a in assignments if a is not None]
        return dict(assignments)

    def assignment(self, name, value):
        return (name.value, value)

    # Values
    def number(self, n):
        return int(n)

    def string(self, s):
        return s.value[1:-1]

    def constant_usage(self, name):
        cname = name.value
        if cname not in self.constants:
            raise ValueError(f"Undefined constant: {cname}")
        return self.constants[cname]

    def value(self, v):
        return v

    # Start
    def start(self, *items):
        result = {}
        for item in items:
            if isinstance(item, dict):
                result.update(item)
        return result
