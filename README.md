# Учебный конфигурационный язык — CLI инструмент

## Проект реализует инструмент командной строки для учебного конфигурационного языка.

Он позволяет:
Парсить конфигурацию с числами, строками, словарями и константами.
Подставлять значения констант на этапе трансформации.
Обнаруживать синтаксические ошибки и неопределённые константы.
Преобразовывать конфигурацию в формат TOML.
Работать как с stdin, так и с файлом конфигурации.
Синтаксис учебного конфигурационного языка
Константы
```
(define NAME value)
```
## Поддерживаются числа, строки, словари.
Вычисляются на этапе трансформации:
```
size := [MAX_SIZE];
```

Словари
```
begin
    key1 := value1;
    key2 := value2;
end
```
### Разделение ; обязательно.

## Числа и строки

Числа:
```
[+-]?\d+
```
Строки:
```
"текст"
```

Комментарии
Многострочные:
```
(comment
это комментарий
который можно игнорировать
)
```
Установка
git clone <репозиторий>
cd config_tool
pip install toml

Использование

Через файл:
Get-Content config.txt | python cli.py
или после обновления CLI (поддержка аргументов):
python cli.py config.txt

Интерактивно:
python cli.py
```
(define MAX 10)

begin
    value := [MAX];
end
```
<Ctrl-Z + Enter>  # завершение ввода в PowerShell

### Примеры конфигураций и вывод в TOML
Веб-сервер

Конфигурация:
```
(define PORT 8080)
(define HOST "localhost")

begin
    server := begin
        host := [HOST];
        port := [PORT];
    end;
end
```


Вывод TOML:
```
[server]
host = "localhost"
port = 8080
```
Игра

Конфигурация:
```
(define MAX_PLAYERS 4)

begin
    game := begi
        level_size := 100;
        max_players := [MAX_PLAYERS];
        time_limit := 600;
    end;
end
```


Вывод TOML:
```
[game]
level_size = 100
max_players = 4
time_limit = 600
```

## Тесты

Проект покрыт тестами с использованием pytest:

Тест	Описание	Ожидаемый результат
test_undefined_constant	Использование неопределённой константы	ValueError: Undefined constant: NAME
test_defined_constant	Определение и использование константы	Правильное подставление значения константы
test_nested_dict	Вложенные словари с константами	Правильная структура словаря и TOML
Запуск тестов
pytest tests/


Ожидаемый вывод:

============================= test session starts ==============================
collected 3 items

tests/test_config.py ...                                               [100%]

============================== 3 passed in 0.25s ==============================

Ошибки

Синтаксическая ошибка:
```
begin
    size := 42
end
```


Вывод:

Error: Unexpected token at line X


Неопределённая константа:
```
begin
    value := [UNDEFINED];
end
```


Вывод:

Error: Undefined constant: UNDEFINED

# Пример кода
## файл cli.py
```
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

```
## файл config_lang.py
```
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

```
## файл test_config.py
```
import pytest
from config_lang import make_parser, ConfigTransformer
from lark.exceptions import VisitError

# --- undefined constant ---
def test_undefined_constant():
    parser = make_parser()
    config = """
    begin
        size := [UNDEFINED];
    end
    """
    tree = parser.parse(config)
    tr = ConfigTransformer()

    # Проверяем, что при трансформации возникает VisitError с сообщением о неопределённой константе
    with pytest.raises(VisitError) as exc_info:
        tr.transform(tree)

    # Проверяем, что текст ошибки содержит нужное сообщение
    assert "Undefined constant: UNDEFINED" in str(exc_info.value)

# --- defined constant ---
def test_defined_constant():
    parser = make_parser()
    config = """
    (define MAX 100)
    begin
        size := [MAX];
        name := "test";
    end
    """
    tree = parser.parse(config)
    tr = ConfigTransformer()
    result = tr.transform(tree)

    assert result == {"size": 100, "name": "test"}

# --- nested dictionaries ---
def test_nested_dict():
    parser = make_parser()
    config = """
    (define PORT 8080)
    (define HOST "localhost")
    begin
        server := begin
            host := [HOST];
            port := [PORT];
            database := begin
                name := "mydb";
                timeout := 30;
            end;
        end;
    end
    """
    tree = parser.parse(config)
    tr = ConfigTransformer()
    result = tr.transform(tree)

    expected = {
        "server": {
            "host": "localhost",
            "port": 8080,
            "database": {
                "name": "mydb",
                "timeout": 30
            }
        }
    }
    assert result == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


```

