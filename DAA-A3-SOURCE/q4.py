"""Q4. Strassen excerpt PDF page 16; helpers and NumPy variant reconstructed."""
from common import Counter, seeded_rng
C=Counter()
def conv(A,B):
    return [[sum(x*y for x,y in zip(row,col)) for col in zip(*B)] for row in A]
def madd(A,B): return [[x+y for x,y in zip(a,b)] for a,b in zip(A,B)]
def msub(A,B): return [[x-y for x,y in zip(a,b)] for a,b in zip(A,B)]
def quad(A):
    h=len(A)//2
    return ([r[:h] for r in A[:h]],[r[h:] for r in A[:h]],
            [r[:h] for r in A[h:]],[r[h:] for r in A[h:]])
def join(A,B,Cc,D):
    return [a+b for a,b in zip(A,B)]+[c+d for c,d in zip(Cc,D)]

def strassen(A, B, cutoff=1):
    n = len(A)
    if n <= cutoff:
        C.mult += n**3; C.add += n*n*(n-1)
        return conv(A, B)
    A11, A12, A21, A22 = quad(A); B11, B12, B21, B22 = quad(B)
    M1 = strassen(madd(A11, A22), madd(B11, B22), cutoff)
    M2 = strassen(madd(A21, A22), B11, cutoff)
    M3 = strassen(A11, msub(B12, B22), cutoff)
    M4 = strassen(A22, msub(B21, B11), cutoff)
    M5 = strassen(madd(A11, A12), B22, cutoff)
    M6 = strassen(msub(A21, A11), madd(B11, B12), cutoff)
    M7 = strassen(msub(A12, A22), madd(B21, B22), cutoff)
    h = n // 2; C.add += 18 * h * h
    C11 = madd(msub(madd(M1, M4), M5), M7); C12 = madd(M3, M5)
    C21 = madd(M2, M4); C22 = madd(msub(madd(M1, M3), M2), M6)
    return join(C11, C12, C21, C22)

def multiply(A,B,cutoff=1):
    n=len(A)
    if cutoff<1 or n<1 or len(B)!=n or any(len(r)!=n for r in A+B):
        raise ValueError('Require equally sized nonempty square matrices and cutoff >= 1')
    N=1 << (n-1).bit_length()
    def pad(M): return [r[:]+[0]*(N-n) for r in M]+[[0]*N for _ in range(N-n)]
    return [r[:n] for r in strassen(pad(A),pad(B),cutoff)[:n]]

def numpy_strassen(A,B,cutoff=128):
    import numpy as np
    A=np.asarray(A,dtype=np.float64); B=np.asarray(B,dtype=np.float64)
    if A.ndim!=2 or A.shape!=B.shape or A.shape[0]!=A.shape[1] or not len(A) or cutoff<1:
        raise ValueError('Require equally sized nonempty square matrices and cutoff >= 1')
    n=len(A); N=1 << (n-1).bit_length()
    A=np.pad(A,((0,N-n),(0,N-n))); B=np.pad(B,((0,N-n),(0,N-n)))
    def rec(A,B):
        n=len(A)
        if n<=cutoff: return A@B
        h=n//2
        a,b,c,d=A[:h,:h],A[:h,h:],A[h:,:h],A[h:,h:]
        e,f,g,j=B[:h,:h],B[:h,h:],B[h:,:h],B[h:,h:]
        m1=rec(a+d,e+j); m2=rec(c+d,e); m3=rec(a,f-j)
        m4=rec(d,g-e); m5=rec(a+b,j); m6=rec(c-a,e+f); m7=rec(b-d,g+j)
        return np.block([[m1+m4-m5+m7,m3+m5],[m2+m4,m1+m3-m2+m6]])
    return rec(A,B)[:n,:n]

if __name__ == '__main__':
    rng=seeded_rng()
    for n in (2,4,8,16):
        A=[[rng.randrange(-5,6) for _ in range(n)] for _ in range(n)]
        B=[[rng.randrange(-5,6) for _ in range(n)] for _ in range(n)]
        C.reset(); assert multiply(A,B)==conv(A,B)
        print('n/multiplications/additions:',n,C.mult,C.add)
