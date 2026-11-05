"""Q6. Excerpts PDF pages 26/28; supporting routines reconstructed. k is zero-based."""
from common import Counter, seeded_rng
C=Counter()
def insertion_sort_count(a):
    a=list(a)
    for i in range(1,len(a)):
        x=a[i]; j=i-1
        while j>=0:
            C.comps+=1
            if a[j]<=x: break
            a[j+1]=a[j]; j-=1
        a[j+1]=x
    return a

def partition3(a,p):
    less=[]; greater=[]; eq=0
    for x in a:
        C.comps+=1  # one three-way classification, PDF convention
        if x<p: less.append(x)
        elif x==p: eq+=1
        else: greater.append(x)
    C.largest_side=max(C.largest_side,max(len(less),len(greater))/len(a))
    return less,eq,greater

def mom_select(a, k):
    n = len(a)
    if not 0<=k<n: raise ValueError('k outside array')
    if n <= 5: return insertion_sort_count(a)[k]
    groups = [a[i:i + 5] for i in range(0, n, 5)]
    meds = [insertion_sort_count(g)[len(g) // 2] for g in groups]
    p = mom_select(meds, len(meds) // 2)
    less, eq, greater = partition3(a, p)
    if k < len(less): return mom_select(less, k)
    if k < len(less) + eq: return p
    return mom_select(greater, k - len(less) - eq)

def quickselect(a,k,strategy='random',rng=None):
    if not 0<=k<len(a): raise ValueError('k outside array')
    rng=rng or seeded_rng(); a=list(a)
    while True:
        C.calls+=1
        if strategy not in ('first','random'): raise ValueError('Unknown strategy')
        p=a[0] if strategy=='first' else rng.choice(a)
        less,eq,greater=partition3(a,p)
        if k<len(less): a=less
        elif k<len(less)+eq: return p
        else: a=greater; k-=len(less)+eq

def all_sums(w):
    sums=[0]
    for x in w: sums += [s+x for s in sums]
    return sums

def mitm_subset(w, target):
    h = len(w) // 2
    L = sorted(all_sums(w[:h])); R = sorted(all_sums(w[h:]))
    i, j = 0, len(R) - 1
    while i < len(L) and j >= 0:
        C.steps+=1
        t = L[i] + R[j]
        if t == target: return True
        if t < target: i += 1
        else: j -= 1
    return False

def brute_subset(w,target):
    # Gray-code enumeration: one item changes between consecutive subsets.
    total=previous=0
    for i in range(1 << len(w)):
        gray=i^(i>>1)
        if i:
            changed=gray^previous; bit=changed.bit_length()-1
            total += w[bit] if gray&changed else -w[bit]
        previous=gray; C.steps+=1
        if total==target: return True
    return False

if __name__ == '__main__':
    rng=seeded_rng(); a=[rng.randrange(10000) for _ in range(1000)]
    for strategy in ('first','random','mom'):
        C.reset(); k=len(a)//2
        v=mom_select(a,k) if strategy=='mom' else quickselect(a,k,strategy,seeded_rng())
        assert v==sorted(a)[k]; print(strategy,'value/comparisons:',v,C.comps)
    for n in (10,18,20):
        w=[rng.randrange(1,100) for _ in range(n)]; target=sum(w)+1
        C.reset(); b=brute_subset(w,target); bc=C.steps
        C.reset(); m=mitm_subset(w,target); assert b==m
        print('n/brute steps/MITM generated sums/scan steps:',n,bc,2**(n//2)+2**(n-n//2),C.steps)
