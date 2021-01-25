import numpy as np



def binomialCoefficient(n, k):
    if k < 0 or k > n:   return 0
    if k == 0 or k == n: return 1

    k = min(k, n - k)  # Take advantage of geometry

    k_range = np.arange(k)
    c = np.prod((n - k_range) / (k_range + 1))

    return c


def bernstein(i, n, t):
    return binomialCoefficient(n, i) * (t**i) * ((1 - t)**(n - i))


def bound(min_val, max_val, value):
    return min(max(value, min_val), max_val)
    

def value_to_percent(min_val, max_val, value):
    return 1.0 - ((max_val - bound(min_val, value, max_val)) / (max_val - min_val))


# Returns a triangle wave function
def triangle(val, amplitude):
    return np.abs((np.fmod(val + (amplitude / 2.0), amplitude)) - (amplitude / 2.0))


# Linear interpolation
# Percent: 0.0 -> 1.0
def lerp(low, high, percent):
    return low * (1.0 - percent) + high*percent


def dist(a, b):
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return (dx*dx + dy*dy)**0.5


def intersect(a, ta, b, tb):
    des = tb[:, 0]*ta[:, 1] - tb[:, 1]*ta[:, 0]
    u = ((b[:, 1] - a[:, 1])*ta[:, 0] + (a[:, 0] - b[:, 0])*ta[:, 1]) / des
    
    b[:, 0] += tb[:, 0]*u
    b[:, 1] += tb[:, 1]*u

    # TODO: Handle des div by 0
    # if abs(des) < 0.00001: return None

    return b