// Native syntax: psi4/driver/inputparser.py at 60c9b2a773c05abc26991c5ed48cf9862cdb4978.
// Python syntax is imported in full, including its interpolation-string modes.
lexer grammar PsithonLexer;

options { superClass = PsithonLexerBase; }
import PythonLexer;

@header {
import re

from antlr4 import InputStream

}

@members {
def prepare_input(self, stream):
    """Apply universal newlines and Psi4 comment stripping, retaining line/columns."""
    if not self.native_input:
        return stream
    source = stream.getText(0, stream.size - 1)
    source = source.replace("\r\n", "\n").replace("\r", "\n")
    # The launcher also accepts an output log and extracts its echoed input.
    # Keep blank lines before the extracted section for diagnostic line numbers.
    if "Psi4: An Open-Source Ab Initio Electronic Structure Package" in source:
        lines = source.split("\n")
        start = next(
            (
                index + 3
                for index, line in enumerate(lines)
                if re.match(r"^\s*?==> Input File <==", line)
            ),
            None,
        )
        stop = next(
            (
                index
                for index in range(start or 0, len(lines))
                if re.match(r"^-{74}", lines[index])
            ),
            None,
        )
        if start is None or stop is None:
            return InputStream("\x00" + source)
        source = "\n" * start + "\n".join(lines[start:stop]) + "\n"
    self._psithon_source = source
    if "#" not in source:
        return InputStream(source)
    # Psi4 protects CFOUR payloads before stripping comments. Its comment regex
    # also removes the character immediately preceding an unescaped hash.
    literal = re.compile(
        r"^(\s*?)cfour[=\s]*(\w*?)\s*\{(.*?)\}",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    chunks = []
    cursor = 0
    for block in literal.finditer(source):
        chunks.append((cursor, block.start()))
        cursor = block.end()
    chunks.append((cursor, len(source)))
    characters = list(source)
    for first, last in chunks:
        for comment in re.finditer(r"(^|[^\\])#.*", source[first:last]):
            for index in range(first + comment.start(), first + comment.end()):
                if characters[index] not in "\r\n":
                    characters[index] = " "
    return InputStream("".join(characters))

}

PSI_MOLECULE
    : {self.native.is_start("molecule")}? [mM][oO][lL][eE][cC][uU][lL][eE]
      {self.native.begin("molecule")} -> pushMode(NATIVE_MODE);
PSI_SET
    : {self.native.is_start("set")}? [sS][eE][tT]
      {self.native.begin("set")} -> pushMode(NATIVE_MODE);
PSI_BASIS
    : {self.native.is_start("basis")}?
      ([bB][aA][sS][iI][sS] ('_' [rR][eE][lL][aA][tT][iI][vV][iI][sS][tT][iI][cC])?
      | [dD][fF]'_'[bB][aA][sS][iI][sS]'_'
        ([sS][cC][fF] | [mM][pP]'2' | [cC][cC] | [sS][aA][pP][tT] | [sS][aA][dD] | [dD][cC][tT]))
      {self.native.begin("basis")} -> pushMode(NATIVE_MODE);
PSI_EXTERNAL
    : {self.native.is_start("external")}? [eE][xX][tT][eE][rR][nN][aA][lL]
      {self.native.begin("external")} -> pushMode(NATIVE_MODE);
PSI_PCM
    : {self.native.is_start("pcm")}? [pP][cC][mM]
      {self.native.begin("pcm")} -> pushMode(NATIVE_MODE);
PSI_CFOUR
    : {self.native.is_start("cfour")}? [cC][fF][oO][uU][rR]
      {self.native.begin("cfour")} -> pushMode(NATIVE_MODE);
PSI_MEMORY
    : {self.native_input}? (ID_START ID_CONTINUE*?)? [mM][eE][mM][oO][rR][yY] D_SPACE+ D_DIGIT* '.'? D_DIGIT+
      D_SPACE* [kKmMgGtTpPbBeE] [iI]? [bB];
// After native comment stripping, Psi4 unescapes hashes. Outside strings this
// creates an ordinary Python comment; native modes retain their own handling.
PSI_ESCAPED_COMMENT
    : {self.native_input}? '\\#' ~[\r\n]* -> type(COMMENT), channel(HIDDEN);
PSI_BARRY_NOTEQUAL
    : '<>';
// Psi4 prepends imports before compiling. A file BOM is consequently no longer
// at Python's permitted encoding-marker position.
BOM : '\uFEFF' -> type(ERRORTOKEN);

// Python 3.15 adds lazy imports; 'lazy' remains usable as an identifier.
NAME_OR_LAZY : 'lazy';

// Native bodies retain physical newlines but do not create Python INDENTs.
// Character sets, rather than duplicate literal tokens, preserve the imported
// Python grammar's literal vocabulary (e.g. Python '{' versus native '{').
mode NATIVE_MODE;
D_WS       : D_INLINE_SPACE+ -> channel(HIDDEN);
D_COMMENT  : [#] ~[\r\n]* -> channel(HIDDEN);
D_GEOMETRY_COMMENT
    : {(self.native.kind == "molecule" and not self._input.getText(
          self._tokenStartCharIndex - self._tokenStartColumn,
          self._tokenStartCharIndex - 1).lstrip().lower().startswith("from_file"))}?
      '\\#' ~[\r\n]* -> type(D_COMMENT), channel(HIDDEN);
D_NEWLINE  : '\r'? '\n' {self.native.newline(self.NEWLINE)};
D_LBRACE   : [{] {self.native.open_brace(self.CFOUR_MODE)};
D_RBRACE   : [}] {self.native.close_brace()};
D_LBRACKET : [\u005B] {self.native.open_array()};
D_RBRACKET : [\u005D] {self.native.close_array()};
D_LPAREN   : [(];
D_RPAREN   : [)];
D_EQUALS   : [=];
D_COMMA    : [,];
D_COLON    : [:];
D_DOLLAR   : [$];
D_AT       : [@];
D_STAR     : [*];
D_PLUS     : [+];
D_MINUS    : [-];
D_SLASH    : [/\\];
D_DOT      : [.];
D_SEPARATOR: '--';
D_UNITS    : [uU][nN][iI][tT][sS]?;
D_NO_COM   : [nN][oO] '_'? [cC][oO][mM];
D_NO_REORIENT: [nN][oO] '_'? [rR][eE][oO][rR][iI][eE][nN][tT];
D_SYMMETRY : [sS][yY][mM][mM][eE][tT][rR][yY];
D_PUBCHEM  : [pP][uU][bB][cC][hH][eE][mM];
D_FROM_FILE: [fF][rR][oO][mM]'_'[fF][iI][lL][eE];
D_EFP      : [eE][fF][pP];
D_GHOST    : [gG][hH];
D_ASSIGN   : [aA][sS][sS][iI][gG][nN];
D_NUMBER   : [+-]? (D_DIGIT+ ('.' D_DIGIT*)? | '.' D_DIGIT+) ([dDeE] [+-]? D_DIGIT+)?;
// Native regex fields use Python re \w, which includes numeric characters
// beyond Python identifiers. Field constraints narrow this shared vocabulary.
D_WORD     : D_WORD_CHARACTER+;
D_HYPHEN_WORD: D_WORD_CHARACTER+ '-' (D_WORD_CHARACTER | '-')*;
D_STRING   : '"' ('\\' . | ~["\\])* '"'
           | '\'' ('\\' . | ~['\\])* '\'';
D_ESC_HASH : '\\#';
// Literal payloads and quotified option expressions can contain punctuation.
// Molecule field productions retain their own restricted token vocabulary.
D_OTHER    : ~[\r\n];

fragment D_WORD_CHARACTER : ID_CONTINUE | D_OTHER_NUMBER;

// inputparser.py deliberately takes CFOUR content literally, through the first
// closing brace. In particular, '#' is data in this mode.
mode CFOUR_MODE;
CFOUR_TEXT : ~[}]+;
CFOUR_END  : [}] {self.native.close_brace()} -> type(D_RBRACE);

fragment D_DIGIT // Unicode 17.0, checked exhaustively against Python 3.15.
    : '\u{30}' .. '\u{39}'
    | '\u{660}' .. '\u{669}'
    | '\u{6F0}' .. '\u{6F9}'
    | '\u{7C0}' .. '\u{7C9}'
    | '\u{966}' .. '\u{96F}'
    | '\u{9E6}' .. '\u{9EF}'
    | '\u{A66}' .. '\u{A6F}'
    | '\u{AE6}' .. '\u{AEF}'
    | '\u{B66}' .. '\u{B6F}'
    | '\u{BE6}' .. '\u{BEF}'
    | '\u{C66}' .. '\u{C6F}'
    | '\u{CE6}' .. '\u{CEF}'
    | '\u{D66}' .. '\u{D6F}'
    | '\u{DE6}' .. '\u{DEF}'
    | '\u{E50}' .. '\u{E59}'
    | '\u{ED0}' .. '\u{ED9}'
    | '\u{F20}' .. '\u{F29}'
    | '\u{1040}' .. '\u{1049}'
    | '\u{1090}' .. '\u{1099}'
    | '\u{17E0}' .. '\u{17E9}'
    | '\u{1810}' .. '\u{1819}'
    | '\u{1946}' .. '\u{194F}'
    | '\u{19D0}' .. '\u{19D9}'
    | '\u{1A80}' .. '\u{1A89}'
    | '\u{1A90}' .. '\u{1A99}'
    | '\u{1B50}' .. '\u{1B59}'
    | '\u{1BB0}' .. '\u{1BB9}'
    | '\u{1C40}' .. '\u{1C49}'
    | '\u{1C50}' .. '\u{1C59}'
    | '\u{A620}' .. '\u{A629}'
    | '\u{A8D0}' .. '\u{A8D9}'
    | '\u{A900}' .. '\u{A909}'
    | '\u{A9D0}' .. '\u{A9D9}'
    | '\u{A9F0}' .. '\u{A9F9}'
    | '\u{AA50}' .. '\u{AA59}'
    | '\u{ABF0}' .. '\u{ABF9}'
    | '\u{FF10}' .. '\u{FF19}'
    | '\u{104A0}' .. '\u{104A9}'
    | '\u{10D30}' .. '\u{10D39}'
    | '\u{10D40}' .. '\u{10D49}'
    | '\u{11066}' .. '\u{1106F}'
    | '\u{110F0}' .. '\u{110F9}'
    | '\u{11136}' .. '\u{1113F}'
    | '\u{111D0}' .. '\u{111D9}'
    | '\u{112F0}' .. '\u{112F9}'
    | '\u{11450}' .. '\u{11459}'
    | '\u{114D0}' .. '\u{114D9}'
    | '\u{11650}' .. '\u{11659}'
    | '\u{116C0}' .. '\u{116C9}'
    | '\u{116D0}' .. '\u{116E3}'
    | '\u{11730}' .. '\u{11739}'
    | '\u{118E0}' .. '\u{118E9}'
    | '\u{11950}' .. '\u{11959}'
    | '\u{11BF0}' .. '\u{11BF9}'
    | '\u{11C50}' .. '\u{11C59}'
    | '\u{11D50}' .. '\u{11D59}'
    | '\u{11DA0}' .. '\u{11DA9}'
    | '\u{11DE0}' .. '\u{11DE9}'
    | '\u{11F50}' .. '\u{11F59}'
    | '\u{16130}' .. '\u{16139}'
    | '\u{16A60}' .. '\u{16A69}'
    | '\u{16AC0}' .. '\u{16AC9}'
    | '\u{16B50}' .. '\u{16B59}'
    | '\u{16D70}' .. '\u{16D79}'
    | '\u{1CCF0}' .. '\u{1CCF9}'
    | '\u{1D7CE}' .. '\u{1D7FF}'
    | '\u{1E140}' .. '\u{1E149}'
    | '\u{1E2F0}' .. '\u{1E2F9}'
    | '\u{1E4F0}' .. '\u{1E4F9}'
    | '\u{1E5F1}' .. '\u{1E5FA}'
    | '\u{1E950}' .. '\u{1E959}'
    | '\u{1FBF0}' .. '\u{1FBF9}'
    ;

fragment D_OTHER_NUMBER // Unicode 17.0, checked exhaustively against Python 3.15.
    : '\u{B2}' .. '\u{B3}'
    | '\u{B9}'
    | '\u{BC}' .. '\u{BE}'
    | '\u{37A}'
    | '\u{9F4}' .. '\u{9F9}'
    | '\u{B72}' .. '\u{B77}'
    | '\u{BF0}' .. '\u{BF2}'
    | '\u{C78}' .. '\u{C7E}'
    | '\u{D58}' .. '\u{D5E}'
    | '\u{D70}' .. '\u{D78}'
    | '\u{F2A}' .. '\u{F33}'
    | '\u{1372}' .. '\u{137C}'
    | '\u{17F0}' .. '\u{17F9}'
    | '\u{2070}'
    | '\u{2074}' .. '\u{2079}'
    | '\u{2080}' .. '\u{2089}'
    | '\u{2150}' .. '\u{215F}'
    | '\u{2189}'
    | '\u{2460}' .. '\u{249B}'
    | '\u{24EA}' .. '\u{24FF}'
    | '\u{2776}' .. '\u{2793}'
    | '\u{2CFD}'
    | '\u{2E2F}'
    | '\u{3192}' .. '\u{3195}'
    | '\u{3220}' .. '\u{3229}'
    | '\u{3248}' .. '\u{324F}'
    | '\u{3251}' .. '\u{325F}'
    | '\u{3280}' .. '\u{3289}'
    | '\u{32B1}' .. '\u{32BF}'
    | '\u{A830}' .. '\u{A835}'
    | '\u{FC5E}' .. '\u{FC63}'
    | '\u{FDFA}' .. '\u{FDFB}'
    | '\u{FE70}'
    | '\u{FE72}'
    | '\u{FE74}'
    | '\u{FE76}'
    | '\u{FE78}'
    | '\u{FE7A}'
    | '\u{FE7C}'
    | '\u{FE7E}'
    | '\u{10107}' .. '\u{10133}'
    | '\u{10175}' .. '\u{10178}'
    | '\u{1018A}' .. '\u{1018B}'
    | '\u{102E1}' .. '\u{102FB}'
    | '\u{10320}' .. '\u{10323}'
    | '\u{10858}' .. '\u{1085F}'
    | '\u{10879}' .. '\u{1087F}'
    | '\u{108A7}' .. '\u{108AF}'
    | '\u{108FB}' .. '\u{108FF}'
    | '\u{10916}' .. '\u{1091B}'
    | '\u{109BC}' .. '\u{109BD}'
    | '\u{109C0}' .. '\u{109CF}'
    | '\u{109D2}' .. '\u{109FF}'
    | '\u{10A40}' .. '\u{10A48}'
    | '\u{10A7D}' .. '\u{10A7E}'
    | '\u{10A9D}' .. '\u{10A9F}'
    | '\u{10AEB}' .. '\u{10AEF}'
    | '\u{10B58}' .. '\u{10B5F}'
    | '\u{10B78}' .. '\u{10B7F}'
    | '\u{10BA9}' .. '\u{10BAF}'
    | '\u{10CFA}' .. '\u{10CFF}'
    | '\u{10E60}' .. '\u{10E7E}'
    | '\u{10F1D}' .. '\u{10F26}'
    | '\u{10F51}' .. '\u{10F54}'
    | '\u{10FC5}' .. '\u{10FCB}'
    | '\u{11052}' .. '\u{11065}'
    | '\u{111E1}' .. '\u{111F4}'
    | '\u{1173A}' .. '\u{1173B}'
    | '\u{118EA}' .. '\u{118F2}'
    | '\u{11C5A}' .. '\u{11C6C}'
    | '\u{11FC0}' .. '\u{11FD4}'
    | '\u{16B5B}' .. '\u{16B61}'
    | '\u{16E80}' .. '\u{16E96}'
    | '\u{1D2C0}' .. '\u{1D2D3}'
    | '\u{1D2E0}' .. '\u{1D2F3}'
    | '\u{1D360}' .. '\u{1D378}'
    | '\u{1E8C7}' .. '\u{1E8CF}'
    | '\u{1EC71}' .. '\u{1ECAB}'
    | '\u{1ECAD}' .. '\u{1ECAF}'
    | '\u{1ECB1}' .. '\u{1ECB4}'
    | '\u{1ED01}' .. '\u{1ED2D}'
    | '\u{1ED2F}' .. '\u{1ED3D}'
    | '\u{1F100}' .. '\u{1F10C}'
    ;

fragment D_INLINE_SPACE // Unicode 17.0 Python whitespace except CR/LF.
    : '\u{9}'
    | '\u{B}' .. '\u{C}'
    | '\u{1C}' .. '\u{20}'
    | '\u{85}'
    | '\u{A0}'
    | '\u{1680}'
    | '\u{2000}' .. '\u{200A}'
    | '\u{2028}' .. '\u{2029}'
    | '\u{202F}'
    | '\u{205F}'
    | '\u{3000}'
    ;

fragment D_SPACE : D_INLINE_SPACE | [\r\n];
