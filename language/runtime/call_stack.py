from language.runtime.frame import Frame
from language.runtime.runtime_errors import RuntimeFunctionError


class CallStack:
    def __init__(self):
        self.frames: list[Frame] = []

    def push(self, frame: Frame) -> None:
        self.frames.append(frame)

    def pop(self) -> Frame:
        if not self.frames:
            raise RuntimeFunctionError("Стек вызовов пуст.")

        return self.frames.pop()

    def current(self) -> Frame:
        if not self.frames:
            raise RuntimeFunctionError("Нет активной функции.")

        return self.frames[-1]

    def __len__(self) -> int:
        return len(self.frames)
