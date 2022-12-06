#!/usr/bin/env python
#
# Input: SQL query
# Output: MongoDB query (pymongo)
# http://docs.mongodb.org/manual/reference/sql-comparison/
# http://www.querymongo.com/
#

from optparse import OptionParser
from sys import stdout, exit as sys_exit

DEBUG = False

def debug_print(func):
    """
    Just a utility decorator to stay out of the way and help with debugging.
    :param func: Name of function.
    :return: function
    """
    def wrapper(*args, **kwargs):
        ret = func(*args, **kwargs)
        if DEBUG:
            stdout.write('\n++Call {} with A:{} K:{}\n++got back {}\n'.format(
                func.__name__, args, kwargs, ret))
            stdout.flush()
        return ret
    return wrapper

def sql_to_spec(query):
    """
    Convert an SQL query to a mongo spec.
    This only supports select statements. For now.
    :param query: String. A SQL query.
    :return: None or a dictionary containing a mongo spec.
    """
    @debug_print
    def fix_token_list(in_list):
        """
        tokens as List is some times deaply nested and hard to deal with.
        Improve parser grouping remove this.
        """
        if isinstance(in_list, list) and len(in_list) == 1 and \
           isinstance(in_list[0], list):
            return fix_token_list(in_list[0])
        else:
            return [item for item in in_list]

    @debug_print
    def select_count_func(*args):
        tokens = args[2]
        return full_select_func(tokens, 'count')

    @debug_print
    def select_distinct_func(*args):
        tokens = args[2]
        return full_select_func(tokens, 'distinct')

    @debug_print
    def select_func(*args):
        tokens = args[2]
        return full_select_func(tokens, 'select')

    def full_select_func(tokens=None, method='select'):
        """
        Take tokens and return a dictionary.
        """
        action = {'distinct': 'distinct',
                  'count': 'count'
                  }.get(method, 'find')
        if tokens is None:
            return
        ret = {action: True, 'fields': {item: 1 for item in fix_token_list(tokens.asList())}}
        if ret['fields'].get('id'):  # Use _id and not id
            # Drop _id from fields since mongo always return _id
            del(ret['fields']['id'])
        else:
            ret['fields']['_id'] = 0
        if "*" in ret['fields'].keys():
            ret['fields'] = {}
        # print(ret)
        return ret

    @debug_print
    def where_func(*args):
        """
        Take tokens and return a dictionary.
        """
        tokens = args[2]
        if tokens is None:
            return
        tokens = fix_token_list(tokens.asList()) + [None, None, None]
        cond = {'!=': '$ne',
                '>': '$gt',
                '>=': '$gte',
                '<': '$lt',
                '<=': '$lte',
                'like': '$regex'}.get(tokens[1])

        find_value = tokens[2].strip('"').strip("'")
        if cond == '$regex':
            if find_value[0] != '%':
                find_value = "^" + find_value
            if find_value[-1] != '%':
                find_value = find_value + "$"
            find_value = find_value.strip("%")

        if cond is None:
            expr = {tokens[0]: find_value}
        else:
            expr = {tokens[0]: {cond: find_value}}
        
        return expr

    @debug_print
    def combine(*args):
        tokens = args[2]
        if tokens:
            tokens = fix_token_list(tokens.asList())
            if len(tokens) == 1:
                return tokens
            else:
                return {'${}'.format(tokens[1]): [tokens[0], tokens[2]]}

    # TODO: Reduce list of imported functions.
    from pyparsing import (Word, alphas, CaselessKeyword, Group, Optional, ZeroOrMore,
                           Forward, Suppress, alphanums, OneOrMore, quotedString,
                           Combine, Keyword, Literal, replaceWith, oneOf, nums,
                           removeQuotes, QuotedString, Dict)

    LPAREN, RPAREN = map(Suppress, "()")
    EXPLAIN = CaselessKeyword('EXPLAIN'
                              ).setParseAction(lambda t: {'explain': True})
    SELECT = Suppress(CaselessKeyword('SELECT'))
    WHERE = Suppress(CaselessKeyword('WHERE'))
    FROM = Suppress(CaselessKeyword('FROM'))
    CONDITIONS = oneOf("= != < > <= >= like", caseless=True)
    #CONDITIONS = (Keyword("=") | Keyword("!=") |
    #              Keyword("<") | Keyword(">") |
    #              Keyword("<=") | Keyword(">="))
    AND = CaselessKeyword('and')
    OR = CaselessKeyword('or')

    word_match = Word(alphanums + "._") | quotedString
    number = Word(nums)
    statement = Group(word_match + CONDITIONS + word_match
                      ).setParseAction(where_func)
    
    select_fields = Group(SELECT + (word_match | Keyword("*")) +
                          ZeroOrMore(Suppress(",") +
                                    (word_match | Keyword("*")))
                          ).setParseAction(select_func)
    
    select_distinct = (SELECT + Suppress(CaselessKeyword('DISTINCT')) + LPAREN
                            + (word_match | Keyword("*"))
                               + ZeroOrMore(Suppress(",")
                               + (word_match | Keyword("*")))
                            + Suppress(RPAREN)).setParseAction(select_distinct_func)

    select_count = (SELECT + Suppress(CaselessKeyword('COUNT')) + LPAREN
                            + (word_match | Keyword("*"))
                               + ZeroOrMore(Suppress(",")
                               + (word_match | Keyword("*")))
                            + Suppress(RPAREN)).setParseAction(select_count_func)
    LIMIT = (Suppress(CaselessKeyword('LIMIT')) + word_match).setParseAction(lambda t: {'limit': t[0]})
    SKIP = (Suppress(CaselessKeyword('SKIP')) + word_match).setParseAction(lambda t: {'skip': t[0]})
    from_table = (FROM + word_match).setParseAction(
        lambda t: {'collection': t.asList()[0]})
    #word = ~(AND | OR) + word_match

    operation_term = (select_distinct | select_count | select_fields)   # place holder for other SQL statements. ALTER, UPDATE, INSERT
    expr = Forward()
    atom = statement | (LPAREN + expr + RPAREN)
    and_term = (OneOrMore(atom) + ZeroOrMore(AND + atom)
                ).setParseAction(combine)
    or_term = (and_term + ZeroOrMore(OR + and_term)).setParseAction(combine)

    where_clause = (WHERE + or_term
                    ).setParseAction(lambda t: {'spec': t[0]})
    list_term = Optional(EXPLAIN) + operation_term + from_table + \
                Optional(where_clause) + Optional(LIMIT) + Optional(SKIP)
    expr << list_term
    
    ret = expr.parseString(query.strip())
    
    query_dict = {}
    query_list = ret.asList()
    
    for extra in query_list:
        query_dict.update(extra)
    
    return query_dict


def spec_str(spec):
    """
    Change a spec to the json object format used in mongo.
    eg. Print dict in python gives: {'a':'b'}
        mongo shell would do {a:'b'}
        Mongo shell can handle both formats but it looks more like the
        official docs to keep to their standard.
    :param spec: Dictionary. A mongo spec.
    :return: String. The spec as it is represended in the mongodb shell examples.
    """

    if spec is None:
        return "{}"
    if isinstance(spec, list):
        out_str = "[" + ', '.join([spec_str(x) for x in spec]) + "]"
    elif isinstance(spec, dict):
        out_str = "{" + ', '.join(["'{}':{}".format(x.replace("'", ""), spec_str(spec[x])
                                                ) for x in sorted(spec)]) + "}"
    elif spec and isinstance(spec, str) and not spec.isdigit():
        out_str = "'" + spec + "'"
    else:
        out_str = spec

    return out_str

@debug_print
def create_mongo_shell_query(query_dict):
    """
    Create the queries similar to what you will us in mongo shell
    :param query_dict: Dictionary. Internal data structure.
    :return: String. The query that you can use in mongo shell.
    """
    if not query_dict.get('collection'):
        return
    shell_query = "db." + query_dict.get('collection') + "."

    if query_dict.get('find'):
        shell_query += 'find({}, {})'.format(spec_str(query_dict.get('spec')),
                                             spec_str(query_dict.get('fields')))
    elif query_dict.get('distinct'):
        shell_query += 'distinct({})'.format(spec_str(",".join(
            [k for k in query_dict.get('fields').keys() if query_dict['fields'][k]])))
    elif query_dict.get('count'):
        shell_query += 'count({})'.format(spec_str(query_dict.get('spec')))
    if query_dict.get('skip'):
        shell_query += ".skip({})".format(query_dict.get('skip'))

    if query_dict.get('limit'):
        shell_query += ".limit({})".format(query_dict.get('limit'))

    if query_dict.get('explain'):
        shell_query += ".explain()"

    return shell_query

if __name__ == '__main__':
    print('OK')