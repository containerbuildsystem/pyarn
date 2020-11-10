tokens = (
    "STRING",
    "COMMENT",
    "NEWLINE",
    "COMMA",
    "COLON",
    "SPACE",
)

t_COMMENT = r"[#]+.*"
t_COMMA = r"[ ]*,[ ]*"
t_COLON = r"[ ]*:[ ]*"
t_SPACE = r"[ ]"


def t_NEWLINE(t):
    r"(\n|\r\n)+"
    t.lexer.lineno += len(t.value)
    return t


# TODO: handle final escaped quotes
def t_STRING(t):
    r'"[^"\n]*"|[a-zA-Z/.-]([^\s\n,]*[^\s\n,:])?'
    if t.value.startswith('"'):
        t.value = t.value[1:-1]
    return t


def t_error(t):
    raise ValueError(f"{t.lexer.lineno}: Invalid token {t.value}")
