import ast
import operator as op


_operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
}


def _eval(node):
    if isinstance(node, ast.Num):  # type: ignore[attr-defined]
        return node.n
    if isinstance(node, ast.BinOp):
        left = _eval(node.left)
        right = _eval(node.right)
        oper = _operators[type(node.op)]
        return oper(left, right)
    if isinstance(node, ast.UnaryOp):
        operand = _eval(node.operand)
        oper = _operators[type(node.op)]
        return oper(operand)
    raise ValueError("Unsupported expression")


def safe_calculate(expression: str) -> str:
    """Safely evaluate a simple arithmetic expression."""
    try:
        tree = ast.parse(expression, mode="eval")
        result = _eval(tree.body)
        return str(result)
    except Exception:
        return "Sorry, I couldn't evaluate that expression."


