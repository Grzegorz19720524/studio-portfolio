from typing import Any


class Stack:
    def __init__(self):
        self._data: list[Any] = []

    def push(self, value: Any) -> None:
        self._data.append(value)

    def pop(self) -> Any:
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._data.pop()

    def peek(self) -> Any:
        if self.is_empty():
            raise IndexError("peek at empty stack")
        return self._data[-1]

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def clear(self) -> None:
        self._data.clear()

    def to_list(self) -> list[Any]:
        return list(reversed(self._data))

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self):
        return reversed(self._data)

    def __repr__(self) -> str:
        return f"Stack(top -> {self._data[::-1]})"


def is_balanced(s: str) -> bool:
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = Stack()
    for ch in s:
        if ch in "([{":
            stack.push(ch)
        elif ch in ")]}":
            if stack.is_empty() or stack.pop() != pairs[ch]:
                return False
    return stack.is_empty()


def evaluate_rpn(tokens: list[str]) -> float:
    ops = {
        "+": lambda a, b: a + b,
        "-": lambda a, b: a - b,
        "*": lambda a, b: a * b,
        "/": lambda a, b: a / b,
        "**": lambda a, b: a ** b,
    }
    stack = Stack()
    for token in tokens:
        if token in ops:
            b, a = stack.pop(), stack.pop()
            stack.push(ops[token](a, b))
        else:
            stack.push(float(token))
    return stack.pop()


def infix_to_rpn(expression: str) -> list[str]:
    precedence = {"+": 1, "-": 1, "*": 2, "/": 2, "**": 3}
    right_assoc = {"**"}
    output, ops = [], Stack()
    tokens = expression.replace("(", "( ").replace(")", " )").split()
    for token in tokens:
        if token == "(":
            ops.push(token)
        elif token == ")":
            while not ops.is_empty() and ops.peek() != "(":
                output.append(ops.pop())
            ops.pop()
        elif token in precedence:
            while (
                not ops.is_empty()
                and ops.peek() in precedence
                and (
                    precedence[ops.peek()] > precedence[token]
                    or (precedence[ops.peek()] == precedence[token] and token not in right_assoc)
                )
            ):
                output.append(ops.pop())
            ops.push(token)
        else:
            output.append(token)
    while not ops.is_empty():
        output.append(ops.pop())
    return output


def sort_stack(stack: Stack) -> Stack:
    sorted_stack = Stack()
    while not stack.is_empty():
        tmp = stack.pop()
        while not sorted_stack.is_empty() and sorted_stack.peek() > tmp:
            stack.push(sorted_stack.pop())
        sorted_stack.push(tmp)
    return sorted_stack


def reverse_stack(stack: Stack) -> Stack:
    result = Stack()
    while not stack.is_empty():
        result.push(stack.pop())
    return result


if __name__ == "__main__":
    s = Stack()
    for v in [1, 2, 3, 4, 5]:
        s.push(v)

    print("stack:       ", s)
    print("peek:        ", s.peek())
    print("pop:         ", s.pop())
    print("len:         ", len(s))
    print("to_list:     ", s.to_list())

    print("\nis_balanced('({[]})'):  ", is_balanced("({[]})"))
    print("is_balanced('({[}])'):  ", is_balanced("({[}])"))
    print("is_balanced('((())'):   ", is_balanced("((())"))
    print("is_balanced(''):        ", is_balanced(""))

    print("\nevaluate_rpn ['3','4','+','2','*']:", evaluate_rpn(["3", "4", "+", "2", "*"]))
    print("evaluate_rpn ['5','1','2','+','4','*','+','3','-']:",
          evaluate_rpn(["5", "1", "2", "+", "4", "*", "+", "3", "-"]))

    expr = "3 + 4 * 2"
    rpn = infix_to_rpn(expr)
    print(f"\ninfix_to_rpn('{expr}'): {rpn}")
    print(f"evaluated:              {evaluate_rpn(rpn)}")

    expr2 = "(3 + 4) * 2"
    rpn2 = infix_to_rpn(expr2)
    print(f"\ninfix_to_rpn('{expr2}'): {rpn2}")
    print(f"evaluated:               {evaluate_rpn(rpn2)}")

    print("\nsort_stack:")
    unsorted = Stack()
    for v in [3, 1, 4, 1, 5, 9, 2, 6]:
        unsorted.push(v)
    sorted_s = sort_stack(unsorted)
    print("sorted (top->bottom):", sorted_s.to_list())

    print("\nreverse_stack:", reverse_stack(sorted_s).to_list())
