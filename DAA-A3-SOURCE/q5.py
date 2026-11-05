"""Q5. closest_dc from PDF page 22; helpers/datasets reconstructed."""
from common import Counter, seeded_rng
C=Counter()
def d2(p,q):
    C.distances+=1
    return (p[0]-q[0])**2+(p[1]-q[1])**2

def brute(P):
    best=(float('inf'),None,None)
    for i in range(len(P)):
        for j in range(i+1,len(P)):
            v=d2(P[i],P[j])
            if v<best[0]: best=(v,P[i],P[j])
    return best

def merge_by_y(L,R):
    out=[]; i=j=0
    while i<len(L) and j<len(R):
        if L[i][1]<=R[j][1]: out.append(L[i]); i+=1
        else: out.append(R[j]); j+=1
    return out+L[i:]+R[j:]

def closest_dc(Px):
    n = len(Px)
    if n <= 3:
        b = brute(Px); return b[0], b[1], b[2], sorted(Px, key=lambda p: p[1])
    mid = n // 2; xm = Px[mid][0]
    dl, pl, ql, Yl = closest_dc(Px[:mid])
    dr, pr, qr, Yr = closest_dc(Px[mid:])
    best = (dl, pl, ql) if dl <= dr else (dr, pr, qr)
    Y = merge_by_y(Yl, Yr)
    d = best[0]
    strip = [p for p in Y if (p[0] - xm) ** 2 < d]
    for a in range(len(strip)):
        b = a + 1
        while b < len(strip) and (strip[b][1] - strip[a][1]) ** 2 < d:
            v = d2(strip[a], strip[b])
            if v < d: d = v; best = (v, strip[a], strip[b])
            b += 1
    return best[0], best[1], best[2], Y

def dataset(n,kind='uniform',rng=None):
    rng=rng or seeded_rng()
    if kind=='uniform': return [(rng.uniform(0,1e6),rng.uniform(0,1e6)) for _ in range(n)]
    if kind=='vertical': return [(rng.uniform(-.001,.001),rng.uniform(0,1e6)) for _ in range(n)]
    if kind=='clustered':
        centers=[(rng.uniform(0,1e6),rng.uniform(0,1e6)) for _ in range(10)]
        out=[]
        for _ in range(n):
            x,y=rng.choice(centers); out.append((rng.gauss(x,1000),rng.gauss(y,1000)))
        return out
    raise ValueError('Unknown dataset')

if __name__ == '__main__':
    for kind in ('uniform','clustered','vertical'):
        for n in (10,50,100,1000):
            P=dataset(n,kind); C.reset(); b=brute(P); bc=C.distances
            C.reset(); d=closest_dc(sorted(P)); assert b[0]==d[0]
            print(kind,'n/brute distances/DC distances/min squared distance:',n,bc,C.distances,d[0])
