#!/usr/bin/env python3

from fpylll import BKZ, IntegerMatrix

inv_mod = lambda a, m : pow(a, m-2, m)

class Curve():
    def __init__(self, p, a, b, q, x0, y0):
        self.p = p
        self.a = a
        self.b = b
        self.b2 = 2*b % self.p
        self.b4 = 2*self.b2 % self.p
        self.q = q
        self.base = (x0, y0)

    def is_on_curve(self, point):
        xx, yy = point
        tmp = xx**2 % self.p
        tmp = xx*tmp % self.p
        tmp = (tmp + xx*self.a + self.b) % self.p
        return (yy**2 - tmp) % self.p == 0

    def single_mul(self, n, P):
        def dbl_xz(self, point):
            # 2P
            x1, z1 = point
            A, B = x1**2 % self.p, z1**2 % self.p
            C = 2*((x1 + z1)**2 - (A + B)) % self.p
            D = self.a*B % self.p
            return ((A - D)**2 - self.b2*B*C) % self.p, ((A + D)*C + self.b4*B**2) % self.p

        def add_xz(self, R0, R1, x0):
            # P + Q
            x1, z1 = R0
            x2, z2 = R1
            A, B = x1*x2 % self.p, z1*z2 % self.p
            C, D = x1*z2 % self.p, x2*z1 % self.p
            A = 2*(C + D)*(A + self.a*B) % self.p
            B = 4*self.b*B**2 % self.p
            C = (C - D)**2 % self.p
            return (A + B - x0*C) % self.p, C

        def y_recovery(self, P, R0, R1):
            x0, y0 = P[:2]
            x1, z1 = R0
            x2, z2 = R1
            A = x0*z1 % self.p
            B = (A - x1)**2 % self.p
            C = x0*x1 % self.p
            D = self.a*z1 % self.p
            A = (A + x1)*(C + D) % self.p
            C = z1*z2 % self.p
            D = 2*y0*C % self.p
            C = self.b2*C % self.p
            return D*x1 % self.p,  (C*z1 + A*z2 - x2*B) % self.p, D*z1 % self.p

        # single scalar mult: n*P
        assert (n > 0 and n < self.q)
        # special case
        if n == self.q - 1: return P[0], self.p - P[1]
        l = int(n).bit_length()
        x1, z1 = P[0], 1
        x2, z2 = dbl_xz(self, [x1, z1])
        R = [(x1, z1), (x2, z2)]
        for i in range(2, l+1):
            bit = (n >> (l-i)) & 1
            R[1-bit] = add_xz(self, R[0], R[1], P[0])
            R[bit] = dbl_xz(self, R[bit])
        x3, y3, z3 = y_recovery(self, P, R[0], R[1])
        t = inv_mod(z3, self.p)
        return x3*t % self.p, y3*t % self.p


    def double_mul(self, n, P, m, Q):
        def dbl_jac(point):
            x1, y1, z1 = point
            A, B = x1**2 % self.p, y1**2 % self.p
            C, D = B**2 % self.p, z1**2 % self.p
            E = 2*((x1 + B)**2 - A - C) % self.p
            A = (3*A + self.a*D**2) % self.p
            F = (A**2 - 2*E) % self.p
            return F, (A*(E - F) - 8*C) % self.p, ((y1 + z1)**2 - B - D) % self.p

        def add_jac(point1, point2):
            x1, y1, z1 = point1
            x2, y2, z2 = point2
            # infinity cases
            if z1 == 0: return point2
            if z2 == 0: return point1
            A, B = z1**2 % self.p, z2**2 % self.p
            C, D = x1*B % self.p, z2*B % self.p
            D = y1*D % self.p
            E = z1*A % self.p
            E = y2*E % self.p
            F = (x2*A - C) % self.p
            G = 4*F**2 % self.p
            H = F*G % self.p
            E = E-D % self.p
            # doubling case
            if F == 0 and E == 0: return dbl_jac(P1)
            E = 2*E % self.p
            C = C*G % self.p
            x3 = (E**2 - H - 2*C) % self.p
            return x3, (E*(C - x3) - 2*D*H) % self.p, ((z1+z2)**2 - A - B)*F % self.p

        # double scalar mult: n*P + m*Q
        l = max(int(n).bit_length(), int(m).bit_length())
        PP = [P[0], P[1], 1]
        QQ = [Q[0], Q[1], 1]
        PQ = add_jac(PP, QQ)
        L = [PP, QQ, PQ]
        T = [1,1,0]
        for i in range(l):
            T = dbl_jac(T)
            val = ((m >> (l-1-i)) & 1) << 1 | ((n >> (l-1-i)) & 1)
            if val != 0:
                T = add_jac(T, L[val-1])
        t = inv_mod(T[2], self.p)
        tsqr = t**2 % self.p
        tcub = tsqr*t % self.p
        return T[0]*tsqr % self.p, T[1]*tcub % self.p


####################
## predefined curves
####################

## P-192
p192 = 0xfffffffffffffffffffffffffffffffeffffffffffffffff
q192 = 0xffffffffffffffffffffffff99def836146bc9b1b4d22831
b192 = 0x64210519e59c80e70fa7e9ab72243049feb8deecc146b9b1
x0192 = 0x188da80eb03090f67cbf20eb43a18800f4ff0afd82ff1012
y0192 = 0x7192b95ffc8da78631011ed6b24cdd573f977a11e794811
secp192r1 = Curve(p192, -3, b192, q192, x0192, y0192)

## P-224
p224 = 0xffffffffffffffffffffffffffffffff000000000000000000000001
q224 = 0xffffffffffffffffffffffffffff16a2e0b8f03e13dd29455c5c2a3d
b224 = 0xb4050a850c04b3abf54132565044b0b7d7bfd8ba270b39432355ffb4
x0224 = 0xb70e0cbd6bb4bf7f321390b94a03c1d356c21122343280d6115c1d21
y0224 = 0xbd376388b5f723fb4c22dfe6cd4375a05a07476444d5819985007e34
secp224r1 = Curve(p224, -3, b224, q224, x0224, y0224)

## P-256
p256 = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
q256 = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
b256 = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
x0256 = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
y0256 = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5
secp256r1 = Curve(p256, -3, b256, q256, x0256, y0256)


## P-384
p384 = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffeffffffff0000000000000000ffffffff
q384 = 0xffffffffffffffffffffffffffffffffffffffffffffffffc7634d81f4372ddf581a0db248b0a77aecec196accc52973
b384 = 0xb3312fa7e23ee7e4988e056be3f82d19181d9c6efe8141120314088f5013875ac656398d8a2ed19d2a85c8edd3ec2aef
x0384 = 0xaa87ca22be8b05378eb1c71ef320ad746e1d3b628ba79b9859f741e082542a385502f25dbf55296c3a545e3872760ab7
y0384 = 0x3617de4a96262c6f5d9e98bf9292dc29f8f41dbd289a147ce9da3113b5f0b8c00a60b1ce1d7e819d7a431d7c90ea0e5f
secp384r1 = Curve(p384, -3, b384, q384, x0384, y0384)

## P-521
p521 = 0x1ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
q521 = 0x1fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffa51868783bf2f966b7fcc0148f709a5d03bb5c9b8899c47aebb6fb71e91386409
b521 = 0x51953eb9618e1c9a1f929a21a0b68540eea2da725b99b315f3b8b489918ef109e156193951ec7e937b1652c0bd3bb1bf073573df883d2c34f1ef451fd46b503f00
x0521 = 0xc6858e06b70404e9cd9e3ecb662395b4429c648139053fb521f828af606b4d3dbaa14b5e77efe75928fe1dc127a2ffa8de3348b3c1856a429bf97e7e31c2e5bd66
y0521 = 0x11839296a789a3bc0045c8a5fb42c7d1bd998f54449579b446817afbd17273e662c97ee72995ef42640c550b9013fad0761353c7086a272c24088be94769fd16650
secp521r1 = Curve(p521, -3, b521, q521, x0521, y0521)


'''
inputs: q: curve parameter (cardinality)
        signatures: list of signatures (m,r,s) given as integers
                    m: hash of signed message
                    (r,s): signature
        l: number of msb or lsb set to 0 of the nonces
        msb: True for msb, False for lsb

output: M: basis matrix of a lattice
'''
def genMatrix_HNP(q, signatures, l, msb):
    n = len(signatures)
    if msb:
        T = [(signatures[i][1]*inv_mod(signatures[i][2], q)) % q for i in range(n)]
        U = [(-inv_mod(signatures[i][2], q)*signatures[i][0]) % q for i in range(n)]
    else:
        T = [(signatures[i][1]*inv_mod(signatures[i][2]*2**l, q)) % q for i in range(n)]
        U = [(-inv_mod(signatures[i][2]*2**l, q)*signatures[i][0]) % q for i in range(n)]
    M = IntegerMatrix(n+2, n+2)
    M[n, n] = 1
    M[n+1, n+1] = q
    for i in range(n):
        M[i, i] = 2**(l+1)*q
        M[n, i] = 2**(l+1)*T[i]
        if msb:
            M[n+1, i] = 2**(l+1)*U[i] + 2**int(q).bit_length()
        else:
            M[n+1, i] = 2**(l+1)*U[i] + q
    return M


'''
inputs: M: basis matrix of a lattice
        curve: instance of the class Curve
        pubkey_point: public point of the signer
output: private key of the signer or -1
'''
def findPrivateKey_HNP(M, curve, pubkey_point, block_size=25):
    Mred = BKZ.reduction(M, BKZ.Param(block_size=block_size))
    for i in range(Mred.nrows):
        row = Mred[i]
        guess = row[-2] % curve.q
        if guess == 0:
            continue
        Q = curve.single_mul(guess, curve.base)
        if Q[0] == pubkey_point[0]:
            if Q[1] == pubkey_point[1]:
                return guess
            else:
                return curve.q - guess
    return -1


'''
check the validity of the signature
'''
def check_signature(curve, pubkey_point, signature):
    m, r, s = signature
    s_inv = inv_mod(s, curve.q)
    u, v = m*s_inv % curve.q, r*s_inv % curve.q
    R = curve.double_mul(u, curve.base, v, pubkey_point)
    return R[0] % curve.q == r


'''
Given a curve, a public point and signatures where the l most
(or least) significant bits of the nonces are set to 0,
returns the private key or -1 if not found
'''
def findkey(curve, pubkey_point, signatures, msb, l, block_size=25):
    M = genMatrix_HNP(curve.q, signatures, l, msb)
    return findPrivateKey_HNP(M, curve, pubkey_point, block_size)
