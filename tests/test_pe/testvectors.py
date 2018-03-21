from random import randint
from itertools import product

__all__ = ['random', 'complete']

def random(func, n, width):
    max = 1 << width
    tests = []
    for i in range(n):
        a = randint(0,max)
        b = randint(0,max)
        d_p = 0  # Ignore for now
        test = [a, b, d_p]
        result = func(*test)
        if not isinstance(result, tuple):
            result = [result]
        else:
            result = list(result)
        test.extend(result)
        tests.append(test)
    return tests

def complete(func, n, width):
    max = 1 << width
    tests = []
    for a in range(n):
        for b in range(n):
            d_p = 0  # Ignore for now
            test = [a, b, d_p]
            result = func(*test)
            if not isinstance(result, tuple):
                result = [result]
            else:
                result = list(result)
            test.extend(result)
            tests.append(test)
    return tests
