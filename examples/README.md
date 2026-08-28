# Демонстрационные программы языка клеточного робота

Все файлы в корне `examples/` должны успешно выполняться командой:

`python -m language.runner examples/<имя>.robot`

Файлы из `examples/robot/` запускаются с тестовым роботом:

`python -m language.runner examples/robot/<имя>.robot --mock-robot`

Файлы из `examples/errors/` специально содержат ошибки и должны завершаться сообщением об ошибке.

## Успешные программы

| Файл | Что демонстрирует | Ожидаемый return |
|---|---|---:|
| 01_literals_types.robot | int, short, short int, bool, true/false/undefined | 18 |
| 02_defaults.robot | значения по умолчанию, vector заданного размера | 6 |
| 03_const.robot | объявление и чтение const | 12 |
| 04_arithmetic.robot | add/sub, одинаковый приоритет | 11 |
| 05_parentheses.robot | операторные скобки | 5 |
| 06_short_expansion.robot | расширение short до int при переполнении вычисления | 32768 |
| 07_bool_conversions.robot | bool ↔ арифметические типы | 0 |
| 08_logic.robot | and, or, not and, not or | 0 |
| 09_comparisons.robot | все четыре оператора сравнения | 4 |
| 10_comparison_undefined.robot | undefined при равенстве | undefined |
| 11_assignment_right_assoc.robot | правоассоциативность set | 14 |
| 12_if_true_false.robot | if/then/else для true и false | 7 |
| 13_if_undefined.robot | при undefined не выполняется ни одна ветвь | 10 |
| 14_do_while.robot | цикл do/while | 15 |
| 15_sizeof.robot | sizeof(bool/short/int/переменной vector) | 13 |
| 16_vector_1d.robot | одномерный vector, чтение и запись | 10 |
| 17_vector_2d.robot | двумерный vector | 12 |
| 18_vector_3d.robot | трёхмерный vector | 6 |
| 19_vector_size_only.robot | vector только с размером и значения по умолчанию | 60 |
| 20_functions.robot | параметры, вызов и return функции | 10 |
| 21_fibonacci.robot | рекурсивный вызов функции | 21 |
| 22_parameter_by_value.robot | скалярный параметр передаётся по значению | 5 |
| 23_vector_parameter_by_value.robot | vector передаётся по значению | 1 |
| 24_case_insensitive.robot | регистронезависимость | 5 |
| 25_identifier_abbreviation.robot | сокращение имени до однозначного префикса | 6 |
| 26_empty_vector.robot | допустимый пустой `vector set {}` | 0 |
| 27_dynamic_vector_size.robot | размер vector из переменной и индекс-выражение | 7 |
| 28_numeric_condition.robot | преобразование чисел в условия if | 3 |
| 29_vector_size_expression.robot | арифметическое выражение в размере vector | 6 |

## Робот

| Файл | Что демонстрирует | Ожидаемый return с MockRobot |
|---|---|---:|
| robot/01_robot_movement.robot | right, left, move, move right, move left как выражения | 1 |
| robot/02_lms.robot | lms как выражение | 0 |
| robot/03_robot_statements.robot | команды робота как отдельные предложения | 1 |
| robot/04_find_exit.robot | ограниченный поисковый цикл: две LMS-проверки и правый приоритет движения | false на стандартном MockRobot |

`robot/04_find_exit.robot` предназначен как интеграционная основа алгоритма поиска. Перед финальной сдачей его следует привязать к точной геометрии треугольного лабиринта и принятому начальному направлению LMS в backend; только после этого корректно фиксировать именно алгоритм левой/правой руки для конкретной модели движения.

## Программы с ожидаемыми ошибками

| Файл | Проверяемая ошибка |
|---|---|
| errors/01_const_assignment.robot | изменение const |
| errors/02_unknown_identifier.robot | неизвестное имя |
| errors/03_ambiguous_abbreviation.robot | неоднозначное сокращение имени |
| errors/04_duplicate_variable.robot | повторное объявление переменной |
| errors/05_duplicate_function.robot | повторное объявление функции |
| errors/06_missing_work.robot | отсутствие точки входа work |
| errors/07_vector_size_mismatch.robot | размер vector не совпадает с инициализатором |
| errors/08_vector_out_of_bounds.robot | статически известный выход за границы |
| errors/09_int_overflow.robot | переполнение int |
| errors/10_short_literal_overflow.robot | литерал не помещается в short |
| errors/11_vector_scalar_operation.robot | арифметика над vector |
| errors/12_wrong_argument_count.robot | неверное количество аргументов |
| errors/13_wrong_argument_type.robot | несовместимый тип аргумента |
| errors/14_missing_semicolon.robot | пропущена `;` |
| errors/15_unexpected_end.robot | лишний `end` |
| errors/16_invalid_character.robot | неизвестный символ lexer'а |
| errors/17_const_vector_element.robot | изменение элемента const vector |
| errors/18_dynamic_out_of_bounds.robot | выход за границы при размере, известном только runtime |
