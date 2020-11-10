# indent
# comment (v1)
# name is a string followed by literals = [",", ":", "\s"]

# left recursion is faster:
# list:
#   item
#   | list ',' item
#   ;
from pyarn.lexer import tokens


def p_blocks(p):
    """blocks : block
              | blocks block"""
    print(f"parsing blocks finally")
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [*p[1], p[2]]


# block is composed by lines??

def p_block(p):
    """block : title spaces members
             | comment"""
    print(f"parsing block.")
    if len(p) == 4:
        # todo split for multi titles and return list or dict
        p[0] = {p[1]: p[3]}
    else:
        p[0] = p[1]


def p_title(p):
    """title : list COLON NEWLINE"""
    print(f"parsing title")
    p[0] = p[1]


def p_list(p):
    """list : STRING
            | list COMMA STRING"""
    print(f"parsing list")
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0].append(p[3])


def p_members(p):
    """members : pair
               | pair spaces members
               | title spaces members"""
    print(f"parsing members")
    if len(p) == 2:
        p[0] = p[1]
    elif isinstance(p[1], list):  # titles
        # todo split for multi titles and return list or dict
        print("TITLE HERE")
        p[0] = {p[1]: p[3]}
    elif isinstance(p[1], dict):  # pairs
        p[1].update(p[3])
        p[0] = p[1]
    else:
        print(f"THIS IS ODD:")
        print(fp[1])
        print(f"ODD:")


def p_pair(p):
    """pair : STRING spaces STRING NEWLINE
            | STRING COLON STRING NEWLINE"""
    print(f"parsing pair")
    p[0] = {p[1]: p[3]}


def p_comment(p):
    """comment : COMMENT NEWLINE
               | spaces COMMENT NEWLINE"""
    print(f"parsing comment")
    p[0] = "Just a comment"


def p_spaces(p):
    """spaces : SPACE
              | spaces SPACE"""
    print(f"parsing spaces")
    if len(p) == 2:
        p[0] = 1
    else:
        p[0] = 1 + p[1]

def p_error(p):
    print(f"error parsing {p.type} at line {p.lineno}:")
    print(f"\tvalue: [{p.value}]")
