#!/usr/bin/env python3
import sys
import toml
from config_lang import make_parser, ConfigTransformer
from lark.exceptions import LarkError, VisitError

def main():
    input_text = sys.stdin.read()
    parser = make_parser()
    transformer = ConfigTransformer()

    try:
        tree = parser.parse(input_text)
        result = transformer.transform(tree)
    except (LarkError, VisitError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Вывод TOML
    toml_text = toml.dumps(result)
    print(toml_text)

if __name__ == "__main__":
    main()
