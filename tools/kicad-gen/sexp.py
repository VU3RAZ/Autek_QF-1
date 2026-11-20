"""Minimal S-expression reader/writer for KiCad files."""


class Sym(str):
    """bare (unquoted) atom"""


def parse(text):
    i, n = 0, len(text)
    stack = [[]]
    while i < n:
        ch = text[i]
        if ch in " \t\r\n":
            i += 1
        elif ch == "(":
            stack.append([])
            i += 1
        elif ch == ")":
            lst = stack.pop()
            stack[-1].append(lst)
            i += 1
        elif ch == '"':
            j = i + 1
            buf = []
            while text[j] != '"':
                if text[j] == "\\":
                    nxt = text[j + 1]
                    buf.append({"n": "\n", "t": "\t", '"': '"', "\\": "\\"}.get(nxt, nxt))
                    j += 2
                else:
                    buf.append(text[j])
                    j += 1
            stack[-1].append("".join(buf))
            i = j + 1
        else:
            j = i
            while j < n and text[j] not in ' \t\r\n()"':
                j += 1
            stack[-1].append(Sym(text[i:j]))
            i = j
    return stack[0]


def q(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def fmt_atom(a):
    if isinstance(a, Sym):
        return str(a)
    if isinstance(a, bool):
        return "yes" if a else "no"
    if isinstance(a, (int, float)):
        if isinstance(a, float):
            s = f"{a:.4f}".rstrip("0").rstrip(".")
            return "0" if s in ("-0", "") else s
        return str(a)
    return q(a)


def dump(e, ind=0):
    if not isinstance(e, list):
        return fmt_atom(e)
    if all(not isinstance(x, list) for x in e) and len(e) < 12:
        return "(" + " ".join(fmt_atom(x) for x in e) + ")"
    parts = []
    head = []
    for x in e:
        if isinstance(x, list):
            break
        head.append(fmt_atom(x))
    out = "(" + " ".join(head)
    for x in e[len(head):]:
        out += "\n" + "  " * (ind + 1) + dump(x, ind + 1)
    return out + "\n" + "  " * ind + ")"


def find(e, key):
    for x in e:
        if isinstance(x, list) and x and x[0] == key:
            return x
    return None


def findall(e, key):
    return [x for x in e if isinstance(x, list) and x and x[0] == key]
