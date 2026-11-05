"""Q7. Self-contained. MaxSub translates PDF page 33 pseudocode directly.
Counters and baseline implementations reconstructed from pages 30-36.
Student A's proposal is intentionally incorrect (missing the crossing case).
"""
from dataclasses import dataclass
import random
@dataclass
class Counter:
    comps: int = 0
    add: int = 0
C=Counter()

def MaxSub(a, lo, hi):
    if lo == hi:
        return (a[lo], a[lo], a[lo], a[lo])
    mid = (lo + hi) // 2
    (lt, lp, ls, lb) = MaxSub(a, lo, mid)
    (rt, rp, rs, rb) = MaxSub(a, mid + 1, hi)
    total = lt + rt
    prefix = max(lp, lt + rp)
    suffix = max(rs, rt + ls)
    best = max(lb, rb, ls + rp)
    C.comps+=4; C.add+=4
    return (total, prefix, suffix, best)

def maximum_subarray(a):
    if not a: raise ValueError('Require a nonempty array')
    return MaxSub(a,0,len(a)-1)[3]

def student_a(a,lo,hi):
    if lo==hi: return a[lo]
    m=(lo+hi)//2; L=student_a(a,lo,m); R=student_a(a,m+1,hi)
    C.comps+=1
    return max(L,R)

def student_b(a,lo,hi):
    if lo==hi: return a[lo]
    m=(lo+hi)//2; L=student_b(a,lo,m); R=student_b(a,m+1,hi)
    s=0; left=float('-inf'); right=float('-inf')
    for i in range(m,lo-1,-1):
        s+=a[i]; left=max(left,s); C.comps+=1; C.add+=1
    s=0
    for i in range(m+1,hi+1):
        s+=a[i]; right=max(right,s); C.comps+=1; C.add+=1
    C.comps+=2; C.add+=1
    return max(L,R,left+right)

def brute_force(a):
    if not a: raise ValueError('Require a nonempty array')
    best=float('-inf')
    for i in range(len(a)):
        s=0
        for j in range(i,len(a)):
            s+=a[j]; best=max(best,s); C.comps+=1; C.add+=1
    return best

def linear_scan(a):
    if not a: raise ValueError('Require a nonempty array')
    current=best=a[0]
    for x in a[1:]:
        current=max(x,current+x); best=max(best,current)
        C.comps+=2; C.add+=1
    return best

if __name__ == '__main__':
    rng=random.Random(2401)
    cases=[[7],[-7],[-1,2],[1,2,3,4,5,6,1,9],[-8,-2,-5,-9,-4,-3],[0]*9,
           [-2,1,-3,4,-1,2,1,-5,4],[-5,2,3,4,5,-1,-9,1],[5,-2,4,-3,4,-2,2],[10,-5,6,7,-20,3,2]]
    wrong=0
    for a in cases+[[rng.randint(-50,50) for _ in range(rng.randint(1,60))] for _ in range(3000)]:
        b=brute_force(a)
        assert maximum_subarray(a)==student_b(a,0,len(a)-1)==linear_scan(a)==b
        wrong+=student_a(a,0,len(a)-1)!=b
    print('Correct designs match brute force on 10 fixed + 3000 random cases.')
    print('Student A failures (including fixed cases):',wrong)
    for n in (8,64,100,1000,1024,10000):
        a=[rng.randint(-1000,1000) for _ in range(n)]; C=Counter(); maximum_subarray(a)
        print('n/final comparisons/predicted:',n,C.comps,4*(n-1))
