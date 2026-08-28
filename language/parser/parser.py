import ply.yacc as yacc

from language.parser import grammar


def build_parser():
    #Построение LR-парсер на основе правил,описанных в grammar.py.
    return yacc.yacc(
        module=grammar,
        start="program",
        debug=False,
        write_tables=False,
    )