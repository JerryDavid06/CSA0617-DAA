"""Q2. Sort excerpts: PDF page 7. Pivot/build helpers reconstructed."""
from common import Counter, seeded_rng

def pick(a, strategy, rng):
    if strategy == 'last': return len(a)-1
    if strategy == 'first': return 0
    if strategy == 'random': return rng.randrange(len(a))
    if strategy in ('median3','median-of-three'):
        return sorted((0,len(a)//2,len(a)-1), key=lambda i:a[i])[1]
    raise ValueError('Unknown pivot strategy')

def quick(a, st, strategy, rng, d=1):
    st.depth = max(st.depth, d)
    if len(a) <= 1: return a
    i = pick(a, strategy, rng); p = a[i]
    rest = a[:i] + a[i+1:]
    less = [x for x in rest if x < p]
    geq = [x for x in rest if x >= p]
    st.comps += len(rest); st.parts.append((len(a), len(less), len(geq)))
    L = quick(less, st, strategy, rng, d+1) if less else []
    R = quick(geq, st, strategy, rng, d+1) if geq else []
    return L + [p] + R

def merge_sort(a, st, d=1):
    st.depth = max(st.depth, d)
    n = len(a)
    if n <= 1: return a
    L = merge_sort(a[:n//2], st, d+1); R = merge_sort(a[n//2:], st, d+1)
    out = []; i = j = 0
    while i < len(L) and j < len(R):
        st.comps += 1
        if L[i] <= R[j]: out.append(L[i]); i += 1
        else: out.append(R[j]); j += 1
    return out + L[i:] + R[j:]

def build_balanced(lo, hi):
    if lo > hi: return []
    m=(lo+hi)//2
    return build_balanced(lo,m-1)+build_balanced(m+1,hi)+[m]

def build_unbalanced(lo, hi):
    if lo > hi: return []
    m=lo+(hi-lo+1)//10
    return build_unbalanced(lo,m-1)+build_unbalanced(m+1,hi)+[m]

if __name__ == '__main__':
    import sys
    sys.setrecursionlimit(20000)
    rng=seeded_rng(); n=255; a=list(range(n)); rng.shuffle(a)
    for name,data in [('balanced',build_balanced(0,n-1)),('random',a),('ascending',list(range(n))),('descending',list(range(n-1,-1,-1))),('90:10',build_unbalanced(0,n-1))]:
        for strategy in ('last','first','median3','random'):
            st=Counter(); assert quick(data,st,strategy,seeded_rng())==sorted(data)
            print(name,strategy,'comparisons/depth/root:',st.comps,st.depth,st.parts[0])
        st=Counter(); assert merge_sort(data,st)==sorted(data)
        print(name,'merge comparisons/depth:',st.comps,st.depth)
