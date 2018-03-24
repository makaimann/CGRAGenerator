from random import randint
import itertools
from collections import OrderedDict, namedtuple

__all__ = ['random', 'complete']

test_input = namedtuple('test_input', ['name', 'value'])
test_output = namedtuple('test_output', ['name', 'value'])

def random(func, n, args, outputs):
    tests = []
    for i in range(n):
        _args = OrderedDict([(k, v()) for k, v in args.items()])
        result = func(**_args)
        test = [test_input(k, v) for k, v in _args.items()] + list(outputs(result))
        tests.append(test)
    return tests

def complete(func, args, outputs):
    tests = []
    keys = [k for k in args.keys()]
    for arg_vals in itertools.product(*(value for value in args.values())):
        _args = OrderedDict([(k, v) for k, v in zip(keys, arg_vals)])
        result = func(**_args)
        test = [test_input(k, v) for k, v in _args.items()] + list(outputs(result))
        tests.append(test)
    return tests
