from random import randint
from itertools import product

__all__ = ['random', 'complete']

def random(func, n, width):
    max = 1 << width
    tests = []
    for i in range(n):
        a = randint(0,max - 1)
        b = randint(0,max - 1)
        d_p = randint(0, 1)
        test = [a, b, d_p]
        result = func(a=a, b=b, d=d_p)
        if not isinstance(result, tuple):
            result = [result]
        else:
            result = list(result)
        test.extend(result)
        tests.append(test)
    return tests

def complete(func, n, width):
    tests = []
    for a in range(n):
        for b in range(n):
            for d_p in range(2):
                test = [a, b, d_p]
                result = func(a=a, b=b, d=d_p)
                if not isinstance(result, tuple):
                    result = [result]
                else:
                    result = list(result)
                test.extend(result)
                tests.append(test)
    return tests
