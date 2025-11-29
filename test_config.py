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
