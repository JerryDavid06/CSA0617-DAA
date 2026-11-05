"""Q3. PDF page 12 algorithm; added counters, padding and carry helpers."""
from common import Counter, seeded_rng, median_ms
C=Counter()
def school(a, b):
    res = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            res[i + j] += ai * bj
    C.mult += len(a) * len(b)
    return res

def karatsuba(a, b, cutoff=1):
    C.calls += 1
    n = len(a)
    if n <= cutoff: return school(a, b)
    h = n // 2
    a0, a1, b0, b1 = a[:h], a[h:], b[:h], b[h:]
    z0 = karatsuba(a0, b0, cutoff)
    z2 = karatsuba(a1, b1, cutoff)
    sa = [x + y for x, y in zip(a0, a1)]
    sb = [x + y for x, y in zip(b0, b1)]
    z1 = karatsuba(sa, sb, cutoff)
    res = [0] * (2 * n - 1)
    for i, v in enumerate(z0): res[i] += v
    for i in range(len(z1)): res[i + h] += z1[i] - z0[i] - z2[i]
    for i, v in enumerate(z2): res[i + 2 * h] += v
    # PDF addition metric excludes school multiply-accumulate operations.
    C.add += 2*h + len(z0) + 3*len(z1) + len(z2)
    return res

def digit_pair(x,y):
    if x < 0 or y < 0: raise ValueError('Use non-negative integers')
    a=[int(v) for v in str(x)[::-1]]; b=[int(v) for v in str(y)[::-1]]
    n=1 << (max(len(a),len(b))-1).bit_length()
    return a+[0]*(n-len(a)),b+[0]*(n-len(b))

def carry_digits(coefficients):
    out=[]; carry=0
    for c in coefficients:
        carry,digit=divmod(c+carry,10); out.append(digit)
    while carry:
        carry,digit=divmod(carry,10); out.append(digit)
    while len(out)>1 and out[-1]==0: out.pop()
    return out

def multiply(x,y,cutoff=1):
    if cutoff < 1: raise ValueError("cutoff must be >= 1")
    a,b=digit_pair(x,y)
    ds=carry_digits(karatsuba(a,b,cutoff))
    return sum(v*10**i for i,v in enumerate(ds))

if __name__ == '__main__':
    rng=seeded_rng()
    for n in (2,4,8,16,64,256):
        a=[rng.randrange(10) for _ in range(n)]; b=[rng.randrange(10) for _ in range(n)]
        C.reset(); expected=school(a,b); standard=C.mult
        C.reset(); assert karatsuba(a,b)==expected
        print('digits/standard mult/Karatsuba mult/add/calls:',n,standard,C.mult,C.add,C.calls)
    print('12345678 * 87654321 =',multiply(12345678,87654321,16))
