import math

def find_root(a, c):
    return (a*c)**(1/2) / a


def length(a, c):
    return (2 * (a*c)**(1/2) * (4*a*c+1)**(1/2) + math.asinh(2 * (a*c)**(1/2))) / (2*a)


def f1(a, c, l):
    '''Returns f(a).'''
    return (2 * (a*c)**(1/2) * (4*a*c+1)**(1/2) + math.asinh(2 * (a*c)**(1/2))) - 2*a*l


def f2(a, c, l):
    '''Returns f'(a).'''
    return 2 * ((c * (1/a+4*c))**(1/2) - l)


def find_a(c, l):
    '''Approximates a using Newton's method.'''

    # The initial guess for a.
    a = 1.0

    # The error term.
    error = 0

    # Run 30 iterations of Newton's method
    for i in range(30):
        a1 = a - f1(a, c, l) / f2(a, c, l)
        error = abs(a1 - a)
        a = a1

        # Convergence completed early.
        if error < 3e-10:
            return a

    return a