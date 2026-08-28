from language.runtime.values import (
    BoolState,
    BoolValue,
    RuntimeValue,
    to_bool,
    to_int,
)


def logical_not(value: RuntimeValue) -> BoolValue:
    state = to_bool(value).value

    if state == BoolState.TRUE:
        return BoolValue(BoolState.FALSE)

    if state == BoolState.FALSE:
        return BoolValue(BoolState.TRUE)

    return BoolValue(BoolState.UNDEFINED)


def logical_and(left: RuntimeValue, right: RuntimeValue) -> BoolValue:
    left_state = to_bool(left).value.value
    right_state = to_bool(right).value.value
    return BoolValue(BoolState(min(left_state, right_state)))


def logical_or(left: RuntimeValue, right: RuntimeValue) -> BoolValue:
    left_state = to_bool(left).value.value
    right_state = to_bool(right).value.value
    return BoolValue(BoolState(max(left_state, right_state)))


def compare(
    operator: str,
    left: RuntimeValue,
    right: RuntimeValue,
) -> BoolValue:
    left_value = to_int(left)
    right_value = to_int(right)

    if left_value == right_value:
        return BoolValue(BoolState.UNDEFINED)

    if operator == "first_smaller":
        result = left_value < right_value
    elif operator == "first_larger":
        result = left_value > right_value
    elif operator == "second_smaller":
        result = right_value < left_value
    elif operator == "second_larger":
        result = right_value > left_value
    else:
        raise ValueError(f"Неизвестный оператор сравнения '{operator}'.")

    return BoolValue(BoolState.TRUE if result else BoolState.FALSE)
