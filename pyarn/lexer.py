tokens = (
    "STRING",
    "COMMENT",
    "COMMA",
    "COLON",
    "INDENT",
    "NEWLINE",
)

t_COMMENT = r"[#]+.*"
t_COMMA = r","
t_COLON = r":"


# TODO: handle final escaped quotes
# Do this first to catch strings with spaces within
def t_STRING(t):
    r'"[^"\n]*"|[a-zA-Z/.-]([^\s\n,]*[^\s\n,:])?'
    if t.value.startswith('"'):
        t.value = t.value[1:-1]
    return t


def t_NEWLINE(t):
    r"(\n|\r\n)+"
    t.lexer.lineno += len(t.value)
    return t


def t_INDENT(t):
    r"([ ][ ])+"
    t.value = len(t.value)//2
    return t


def t_spaces(t):
    r"[ ]"
    pass


def t_error(t):
    raise ValueError(f"{t.lexer.lineno}: Invalid token {t.value}")
