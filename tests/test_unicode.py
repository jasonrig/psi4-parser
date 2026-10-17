"""Check the complete Unicode identifier tables against the target interpreter."""

import re
from pathlib import Path


def _points(fragment: str) -> set[int]:
    pattern = r"'\\u\{([0-9A-F]+)\}'(?:\s*\.\.\s*'\\u\{([0-9A-F]+)\}')?"
    result: set[int] = set()
    for match in re.finditer(pattern, fragment):
        first = int(match.group(1), 16)
        last = int(match.group(2) or match.group(1), 16)
        result.update(range(first, last + 1))
    return result


def test_complete_identifier_tables() -> None:
    """Cover every Unicode code point, including non-BMP and combining characters."""
    grammar = (
        Path(__file__).resolve().parents[1] / "grammar/PythonLexer.g4"
    ).read_text()
    prefix, start_fragment = grammar.split("fragment ID_START //")
    continue_fragment = prefix.split("fragment ID_CONTINUE //")[1]
    starters = _points(start_fragment)
    continuations = starters | _points(continue_fragment)

    assert starters == {point for point in range(0x110000) if chr(point).isidentifier()}
    assert continuations == {
        point for point in range(0x110000) if ("A" + chr(point)).isidentifier()
    }


def test_complete_native_character_tables() -> None:
    """Match native decimal digits and numeric word characters to Python regexes."""
    grammar = (
        Path(__file__).resolve().parents[1] / "grammar/PsithonLexer.g4"
    ).read_text()
    digits, numbers = grammar.split("fragment D_DIGIT //")[1].split(
        "fragment D_OTHER_NUMBER //"
    )
    numbers, spaces = numbers.split("fragment D_INLINE_SPACE //")

    assert _points(digits) == {
        point for point in range(0x110000) if chr(point).isdecimal()
    }
    assert _points(numbers) == {
        point
        for point in range(0x110000)
        if chr(point).isalnum() and not ("A" + chr(point)).isidentifier()
    }
    assert _points(spaces) == {
        point
        for point in range(0x110000)
        if chr(point).isspace() and chr(point) not in "\r\n"
    }
