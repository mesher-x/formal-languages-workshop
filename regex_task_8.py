# Мещеряков Евгений, 696

# Задача 8.
# Даны α, буква x и натуральное число k. Вывести длину кратчайшего слова из языка L, содержащего суффикс x^k.

# Задача сводится к поиску длины кратчайшего слова в L^R, имеющего искомый префикс.
# L^R задается regex^R. Лексемы regex^R соответствуют лексемам regex,
# где для лексем с операцией '.' обращён порядок операндов в листе operands

from collections import deque
from operator import itemgetter


class Lexeme:
    def __init__(self, id, operation, operands):
        self.id = id
        self.operation = operation
        self.operands = operands
        self.shortest_word_len_with_prefix = []


class IncorrectRPN(Exception):
    def __init__(self):
        self.message = 'обратная польская нотация регулярного выражения некорректна'


def main():
    regex_rpn, symbol, degree = input().split()
    degree = int(degree)
    if symbol not in {'a', 'b', 'c'} or has_not_allowed_character(regex_rpn):
        print('недопустимый символ')
        exit(0)
    if degree <= 0:
        print('некорректная степень')
        exit(0)
    try:
        length = get_shortest_word_len_with_suffix(regex_rpn, symbol, degree)
        if length > 0:     # считаю, что в условии натуральные числа без нуля
            print(length)
        else:
            print('INF')
    except IncorrectRPN as e:
        print(e.message)


def has_not_allowed_character(s):
    for ch in s:
        if ch not in {'a', 'b', 'c', '.', '*', '+'}:
            return True
    return False


# нотация не корректна => кидает исключение
def get_shortest_word_len_with_suffix(regex_rpn, symbol, degree):
    lexemes, calculation_priority = get_lexemes_and_priority(regex_rpn)
    # сведение к задаче поиска кратчайшего слова с префиксом
    for lexeme in lexemes:
        if lexeme.operation == '.':
            lexeme.operands.reverse()
    calculation_priority.sort(key=itemgetter(1))    # пары вида [lexeme_id, priority]
    shortest_word_len_with_prefix = calculate_shortest_word_len_with_prefix(lexemes, calculation_priority, symbol,
                                                                            degree)
    return shortest_word_len_with_prefix[degree]


# получает набор лексем из регулярного выражения в обратной польской нотации
# нотация не корректна => кидает исключение
def get_lexemes_and_priority(regex_rpn):
    lexemes = []
    stack = deque()
    lexeme_id = 0
    calculation_priority = []
    for character in regex_rpn:
        if character == '.':
            try:
                second_operand = stack.pop()
                first_operand = stack.pop()
            except IndexError:
                raise IncorrectRPN
            calculation_priority.append([lexeme_id, max(get_priority(calculation_priority, first_operand.id),
                                                        get_priority(calculation_priority, second_operand.id)) + 1])
            operation = '.'
            operands = [first_operand.id, second_operand.id]
        elif character == '+':
            try:
                one_operand = stack.pop()
                another_operand = stack.pop()
            except IndexError:
                raise IncorrectRPN
            calculation_priority.append([lexeme_id, max(get_priority(calculation_priority, one_operand.id),
                                                        get_priority(calculation_priority, another_operand.id)) + 1])
            operation = '+'
            operands = [one_operand.id, another_operand.id]
        elif character == '*':
            try:
                operand = stack.pop()
            except IndexError:
                raise IncorrectRPN
            calculation_priority.append([lexeme_id, get_priority(calculation_priority, operand.id) + 1])
            operation = '*'
            operands = [operand.id]
        else:
            calculation_priority.append([lexeme_id, 0])
            operation = None
            operands = [character]
        lexeme = Lexeme(lexeme_id, operation, operands)
        stack.append(lexeme)
        lexemes.append(lexeme)
        lexeme_id += 1
    if len(stack) != 1:
        raise IncorrectRPN
    return lexemes, calculation_priority


def get_priority(calculation_priority, lexeme_id):
    index = 0
    while calculation_priority[index][0] != lexeme_id:
        index += 1
    return calculation_priority[index][1]


# вычисляет кратчайшие длины слов из языка с префиксом symbol^k, k = 0..degree
def calculate_shortest_word_len_with_prefix(lexemes, calculation_priority, symbol, degree):
    for lexeme_id, priority in calculation_priority:
        lexeme = lexemes[lexeme_id]
        lexeme.shortest_word_len_with_prefix = (degree + 1) * [-1]
        if lexeme.operation is None:
            if lexeme.operands[0] == '1':
                lexeme.shortest_word_len_with_prefix[0] = 0
            elif lexeme.operands[0] == symbol:
                lexeme.shortest_word_len_with_prefix[0] = 1
                lexeme.shortest_word_len_with_prefix[1] = 1
            else:
                lexeme.shortest_word_len_with_prefix[0] = 1
        elif lexeme.operation == '+':
            one = lexemes[lexeme.operands[0]].shortest_word_len_with_prefix
            another = lexemes[lexeme.operands[1]].shortest_word_len_with_prefix
            for prefix_len in range(degree + 1):
                if one[prefix_len] != -1:
                    if another[prefix_len] != -1:
                        lexeme.shortest_word_len_with_prefix[prefix_len] = min(one[prefix_len],
                                                                                  another[prefix_len])
                    else:
                        lexeme.shortest_word_len_with_prefix[prefix_len] = one[prefix_len]
                else:
                    if another[prefix_len] != -1:
                        lexeme.shortest_word_len_with_prefix[prefix_len] = another[prefix_len]
        elif lexeme.operation == '.':
                calculate_concatenation(lexeme.shortest_word_len_with_prefix,
                                        lexemes[lexeme.operands[0]].shortest_word_len_with_prefix,
                                        lexemes[lexeme.operands[1]].shortest_word_len_with_prefix)
        else:  # lexeme.operation == '*'
            operand = lexemes[lexeme.operands[0]].shortest_word_len_with_prefix
            lexeme.shortest_word_len_with_prefix = operand
            lexeme.shortest_word_len_with_prefix[0] = 0
            last_star_degree = list(operand)
            for star_degree in range(2, degree + 1):
                calculate_concatenation(lexeme.shortest_word_len_with_prefix,
                                        last_star_degree,
                                        operand)
                last_star_degree = list(lexeme.shortest_word_len_with_prefix)
    return lexemes[len(lexemes) - 1].shortest_word_len_with_prefix


def calculate_concatenation(to_calculate, first, second):
    degree = len(to_calculate) - 1
    for first_prefix_len in range(degree + 1):
        for second_prefix_len in range(degree + 1):
            if first[first_prefix_len] != -1 and second[second_prefix_len] != -1:
                if (to_calculate[first_prefix_len] == -1
                        or to_calculate[first_prefix_len] > first[first_prefix_len] + second[second_prefix_len]):
                    to_calculate[first_prefix_len] = first[first_prefix_len] + second[second_prefix_len]
                to_calc_prefix_len = min(first_prefix_len + second_prefix_len, degree)
                if (first[first_prefix_len] == first_prefix_len
                    and (to_calculate[to_calc_prefix_len] == -1
                         or to_calculate[to_calc_prefix_len] > first_prefix_len + second[second_prefix_len])):
                    to_calculate[to_calc_prefix_len] = first_prefix_len + second[second_prefix_len]
    restore_invariant(to_calculate)


# if 0 <= i <= i + k <= degree and shortest_word_len_with_prefix[i] != -1 and shortest_word_len_witgh_prefix[i+k] != -1
# then shortest_word_len_with_prefix[i] <= shortest_word_len_witgh_prefix[i + k],
def restore_invariant(shortest_word_len_with_prefix):
    degree = len(shortest_word_len_with_prefix) - 1
    prefix_len = degree
    while shortest_word_len_with_prefix[prefix_len] == -1:
        prefix_len -= 1
    if prefix_len <= 0:
        return
    suffix_min = shortest_word_len_with_prefix[prefix_len]
    while prefix_len >= 0:
        if shortest_word_len_with_prefix[prefix_len] == -1 or shortest_word_len_with_prefix[prefix_len] > suffix_min:
            shortest_word_len_with_prefix[prefix_len] = suffix_min
        else:
            suffix_min = shortest_word_len_with_prefix[prefix_len]
        prefix_len -= 1


if __name__ == "__main__":
    main()
