"""Q1. Core excerpts: PDF pages 2 and 5. Helpers/demo reconstructed."""
from common import seeded_rng

def maxmin_dc(a, lo, hi, cnt):
    if lo == hi:  # 1 element: 0 comparisons
        return a[lo], a[lo]
    if hi == lo + 1:  # 2 elements: 1 comparison
        cnt[0] += 1
        return (a[lo], a[hi]) if a[lo] < a[hi] else (a[hi], a[lo])
    mid = (lo + hi) // 2
    mn1, mx1 = maxmin_dc(a, lo, mid, cnt)
    mn2, mx2 = maxmin_dc(a, mid + 1, hi, cnt)
    cnt[0] += 2
    return min(mn1, mn2), max(mx1, mx2)

def maxmin_power(a, lo, hi, cnt):
    n=hi-lo+1
    if n <= 2: return maxmin_dc(a, lo, hi, cnt)
    left=1 << ((n-1).bit_length()-1)
    mn1,mx1=maxmin_power(a,lo,lo+left-1,cnt)
    mn2,mx2=maxmin_power(a,lo+left,hi,cnt)
    cnt[0]+=2
    return min(mn1,mn2),max(mx1,mx2)

def bsearch(a, lo, hi, t, cnt):
    if lo > hi: return -1
    mid = lo + (hi - lo) // 2
    cnt[0] += 1  # one three-way probe, as in the PDF
    if a[mid] == t: return mid
    if t < a[mid]: return bsearch(a, lo, mid - 1, t, cnt)
    return bsearch(a, mid + 1, hi, t, cnt)

if __name__ == '__main__':
    rng=seeded_rng()
    for n in (8,64,100,1000,1024,10000):
        a=[rng.randrange(1000000) for _ in range(n)]; c=[0]; d=[0]
        assert maxmin_dc(a,0,n-1,c)==(min(a),max(a))
        assert maxmin_power(a,0,n-1,d)==(min(a),max(a))
        print('n, naive, middle split, power split:',n,2*(n-1),c[0],d[0])
    a=list(range(0,2000,2))
    for t in (0,998,1998,999):
        c=[0]; print('target, index, probes:',t,bsearch(a,0,len(a)-1,t,c),c[0])
