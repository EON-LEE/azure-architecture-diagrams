"""Safe arithmetic for spec values such as `r1 + 20` or `lakehouse.bottom`."""
import ast
import operator

_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}


class ExprError(ValueError):
    pass


def evaluate(value, lookup):
    """Return a float. `lookup(name, attr)` resolves `name` or `name.attr`."""
    if isinstance(value, bool):
        raise ExprError(f"expected a number, got {value!r}")
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str):
        raise ExprError(f"expected a number or expression, got {value!r}")
    try:
        tree = ast.parse(value.strip(), mode="eval")
    except SyntaxError as exc:
        raise ExprError(f"invalid expression {value!r}") from exc
    return _eval(tree.body, lookup, value)


def _eval(node, lookup, src):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) \
            and not isinstance(node.value, bool):
        return float(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left, lookup, src), _eval(node.right, lookup, src))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        v = _eval(node.operand, lookup, src)
        return -v if isinstance(node.op, ast.USub) else v
    if isinstance(node, ast.Name):
        return float(lookup(node.id, None))
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        return float(lookup(node.value.id, node.attr))
    raise ExprError(f"unsupported expression {src!r} (use numbers, names, name.attr, + - * /)")
