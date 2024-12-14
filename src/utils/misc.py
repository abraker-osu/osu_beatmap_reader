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


def catmull(ps, t):
    # https://github.com/ppy/osu-framework/blob/050a0b8639c9bd723100288a53923547ce87d487/osu.Framework/Utils/PathApproximator.cs#L449
    t2 = t * t
    t3 = t2 * t
    return 0.5 * (
        2 * ps[1]
        + (ps[2] - ps[0]) * t
        + (2 * ps[0] - 5 * ps[1] + 4 * ps[2] - ps[3]) * t2
        + (ps[3] - 3 * ps[2] + 3 * ps[1] - ps[0]) * t3
    )


def bound(min_val, max_val, value):
    return min(max(value, min_val), max_val)


def frange(start, stop, step):
    curr = start
    while curr < stop:
        yield curr
        curr += step
    

def binary_search(values, value):
    low = 0
    high = len(values)
    while low < high:
        mid = (low + high) // 2
        if values[mid] < value:
            low = mid + 1
        elif values[mid] > value:
            high = mid
        else:
            return mid
    return low


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


def intersect(a, ta, b, tb, precision):
    des = tb[0]*ta[1] - tb[1]*ta[0]
    if abs(des) < precision: return None

    u = ((b[1] - a[1])*ta[0] + (a[0] - b[0])*ta[1]) / des
    return b + tb*u
