#!/usr/bin/env python
# On 20121129
# Critical Line Algorithm
# by MLdP <lopezdeprado@lbl.gov>
import numpy as np


# ---------------------------------------------------------------
# ---------------------------------------------------------------
class CLA:
    def __init__(self, mean, covar, lB, uB):
        # Initialize the class
        self.mean = mean
        self.covar = covar
        self.lB = lB
        self.uB = uB
        self.w = []  # solution
        self.l = []  # lambdas
        self.g = []  # gammas
        self.f = []  # free weights

    # ---------------------------------------------------------------
    def solve(self):
        # Compute the turning points,free sets and weights
        f, w = self.initAlgo()
        self.w.append(np.copy(w))  # store solution
        self.l.append(-np.inf)
        self.g.append(None)
        self.f.append(f[:])
        while True:
            # 1) case a): Bound one free weight
            l_in = -np.inf
            if len(f) > 1:
                covarF, covarFB, meanF, wB = self.getMatrices(f)
                covarF_inv = np.linalg.inv(covarF)
                j = 0
                for i in f:
                    l, bi = self.computeLambda(
                        covarF_inv, covarFB, meanF, wB, j, [self.lB[i], self.uB[i]]
                    )
                    if l > l_in:
                        l_in, i_in, bi_in = l, i, bi
                    j += 1
            # 2) case b): Free one bounded weight
            l_out = -np.inf
            if len(f) < self.mean.shape[0]:
                b = self.getB(f)
                for i in b:
                    covarF, covarFB, meanF, wB = self.getMatrices(f + [i])
                    covarF_inv = np.linalg.inv(covarF)
                    l, bi = self.computeLambda(
                        covarF_inv,
                        covarFB,
                        meanF,
                        wB,
                        meanF.shape[0] - 1,
                        self.w[-1][i],
                    )
                    if (self.l[-1] == -np.inf or l < self.l[-1]) and l > l_out:
                        l_out, i_out = l, i
            # 3) decide lambda
            if (l_in == -np.inf or l_in < 0) and (l_out == -np.inf or l_out < 0):
                break
            if l_in > l_out:
                # If it's the first elment and it's Nan (-np.inf) replace it
                if len(self.l) == 1 and self.l[0] == -np.inf:
                    self.l[0] = l_in
                else:
                    self.l.append(l_in)
                f.remove(i_in)
                w[i_in] = bi_in  # set value at the correct boundary
            else:
                # If it's the first elment and it's Nan (-np.inf) replace it
                if len(self.l) == 1 and self.l[0] == -np.inf:
                    self.l[0] = l_out
                else:
                    self.l.append(l_out)
                f.append(i_out)
            # 4) compute solution vector
            covarF, covarFB, meanF, wB = self.getMatrices(f)
            covarF_inv = np.linalg.inv(covarF)
            wF, g = self.computeW(covarF_inv, covarFB, meanF, wB)
            for i in range(len(f)):
                w[f[i]] = wF[i]
            self.w.append(np.copy(w))  # store solution
            self.g.append(g)
            self.f.append(f[:])
            if len(f) == self.mean.shape[0]:
                # 5) minimum variance solution
                wF, g = self.computeW(covarF_inv, covarFB, np.zeros(meanF.shape), wB)
                for i in range(len(f)):
                    w[f[i]] = wF[i]
                self.w.append(np.copy(w))  # store solution
                self.g.append(g)
                self.f.append(f[:])
        # Remove first element from weights (it's a duplicate)
        self.w = self.w[1:]
        # If we miss the last lambda insert it
        if len(self.l) < len(self.w):
            self.l += [0.0]

    # ---------------------------------------------------------------
    def initAlgo(self):
        # Initialize the algo
        # 1) Form structured array
        a = np.zeros((self.mean.shape[0]), dtype=[("id", int), ("mu", float)])
        b = [self.mean[i][0] for i in range(self.mean.shape[0])]  # dump array into list
        a[:] = list(zip(range(self.mean.shape[0]), b))  # fill structured array
        # 2) Sort structured array
        b = np.sort(a, order="mu")
        # 3) First free weight
        i, w = b.shape[0], np.copy(self.lB)
        while sum(w) < 1:
            i -= 1
            w[b[i][0]] = self.uB[b[i][0]]
        w[b[i][0]] += 1 - sum(w)
        return [b[i][0]], w

    # ---------------------------------------------------------------
    def computeBi(self, c, bi):
        if c > 0:
            bi = bi[1]
        if c < 0:
            bi = bi[0]
        return bi

    # ---------------------------------------------------------------
    def computeW(self, covarF_inv, covarFB, meanF, wB):
        # 1) compute gamma
        onesF = np.ones(meanF.shape)
        g1 = np.dot(np.dot(onesF.T, covarF_inv), meanF)
        g2 = np.dot(np.dot(onesF.T, covarF_inv), onesF)
        if wB is None:
            g, w1 = float(-self.l[-1] * g1 / g2 + 1 / g2), 0
        else:
            onesB = np.ones(wB.shape)
            g3 = np.dot(onesB.T, wB)
            g4 = np.dot(covarF_inv, covarFB)
            w1 = np.dot(g4, wB)
            g4 = np.dot(onesF.T, w1)
            g = float(-self.l[-1] * g1 / g2 + (1 - g3 + g4) / g2)
        # 2) compute weights
        w2 = np.dot(covarF_inv, onesF)
        w3 = np.dot(covarF_inv, meanF)
        return -w1 + g * w2 + self.l[-1] * w3, g

    # ---------------------------------------------------------------
    def computeLambda(self, covarF_inv, covarFB, meanF, wB, i, bi):
        # 1) C
        onesF = np.ones(meanF.shape)
        c1 = np.dot(np.dot(onesF.T, covarF_inv), onesF)
        c2 = np.dot(covarF_inv, meanF)
        c3 = np.dot(np.dot(onesF.T, covarF_inv), meanF)
        c4 = np.dot(covarF_inv, onesF)
        c = -c1 * c2[i] + c3 * c4[i]
        if c == 0:
            return
        # 2) bi
        if type(bi) == list:
            bi = self.computeBi(c, bi)
        # 3) Lambda
        if wB is None:
            # All free assets
            return float((c4[i] - c1 * bi) / c), bi
        else:
            onesB = np.ones(wB.shape)
            l1 = np.dot(onesB.T, wB)
            l2 = np.dot(covarF_inv, covarFB)
            l3 = np.dot(l2, wB)
            l2 = np.dot(onesF.T, l3)
            return float(((1 - l1 + l2) * c4[i] - c1 * (bi + l3[i])) / c), bi

    # ---------------------------------------------------------------
    def getMatrices(self, f):
        # Slice covarF,covarFB,covarB,meanF,meanB,wF,wB
        covarF = self.reduceMatrix(self.covar, f, f)
        meanF = self.reduceMatrix(self.mean, f, [0])
        b = self.getB(f)
        covarFB = self.reduceMatrix(self.covar, f, b)
        wB = self.reduceMatrix(self.w[-1], b, [0])
        return covarF, covarFB, meanF, wB

    # ---------------------------------------------------------------
    def getB(self, f):
        return self.diffLists(np.arange(self.mean.shape[0]), f)

    # ---------------------------------------------------------------
    def diffLists(self, list1, list2):
        return list(set(list1) - set(list2))

    # ---------------------------------------------------------------
    def reduceMatrix(self, matrix, listX, listY):
        # Reduce a matrix to the provided list of rows and columns
        if len(listX) == 0 or len(listY) == 0:
            return
        matrix_ = matrix[:, listY[0] : listY[0] + 1]
        for i in listY[1:]:
            a = matrix[:, i : i + 1]
            matrix_ = np.append(matrix_, a, 1)
        matrix__ = matrix_[listX[0] : listX[0] + 1, :]
        for i in listX[1:]:
            a = matrix_[i : i + 1, :]
            matrix__ = np.append(matrix__, a, 0)
        return matrix__

    # ---------------------------------------------------------------
    def getMinVar(self):
        # Get the minimum variance solution
        var = []
        for w in self.w:
            a = np.dot(np.dot(w.T, self.covar), w)
            var.append(a)
        return min(var) ** 0.5, self.w[var.index(min(var))]

    # ---------------------------------------------------------------
    def getMaxSR(self):
        # Get the max Sharpe ratio portfolio
        # 1) Compute the local max SR portfolio between any two neighbor turning points
        w_sr, sr = [], []
        for i in range(len(self.w) - 1):
            w0 = np.copy(self.w[i])
            w1 = np.copy(self.w[i + 1])
            kargs = {"minimum": False, "args": (w0, w1)}
            a, b = self.goldenSection(self.evalSR, 0, 1, **kargs)
            w_sr.append(a * w0 + (1 - a) * w1)
            sr.append(b)
        return max(sr), w_sr[sr.index(max(sr))]

    # ---------------------------------------------------------------
    def evalSR(self, a, w0, w1):
        # Evaluate SR of the portfolio within the convex combination
        w = a * w0 + (1 - a) * w1
        b = np.dot(w.ravel(), self.mean)[0]
        c = np.sqrt(np.dot(np.dot(w.ravel(), self.covar), w.ravel()))
        return b / c

    # ---------------------------------------------------------------
    def goldenSection(self, obj, a, b, **kargs):
        # Golden section method. Maximum if kargs['minimum']==False is passed
        # from math import log,ceil
        tol, sign, args = 1.0e-9, 1, None
        if "minimum" in kargs and kargs["minimum"] == False:
            sign = -1
        if "args" in kargs:
            args = kargs["args"]
        numIter = int(np.ceil(-2.078087 * np.log(tol / np.abs(b - a))))
        r = 0.618033989
        c = 1.0 - r
        # Initialize
        x1 = r * a + c * b
        x2 = c * a + r * b
        f1 = sign * obj(x1, *args)
        f2 = sign * obj(x2, *args)
        # Loop
        for i in range(numIter):
            if f1 > f2:
                a = x1
                x1 = x2
                f1 = f2
                x2 = c * a + r * b
                f2 = sign * obj(x2, *args)
            else:
                b = x2
                x2 = x1
                f2 = f1
                x1 = r * a + c * b
                f1 = sign * obj(x1, *args)
        if f1 < f2:
            return x1, sign * f1
        else:
            return x2, sign * f2

    # ---------------------------------------------------------------
    def efFrontier(self, points):
        # Get the efficient frontier
        mu, sigma, weights = [], [], []
        a = np.linspace(0, 1, points // len(self.w))[
            :-1
        ]  # remove the 1, to avoid duplications
        b = np.arange(len(self.w) - 1)
        for i in b:
            w0, w1 = self.w[i], self.w[i + 1]
            if i == b[-1]:
                a = np.linspace(
                    0, 1, points // len(self.w)
                )  # include the 1 in the last iteration
            for j in a:
                w = w1 * j + (1 - j) * w0
                weights.append(np.copy(w))
                mu.append(np.dot(w.T, self.mean)[0, 0])
                sigma.append(np.dot(np.dot(w.T, self.covar), w)[0, 0] ** 0.5)
        return mu, sigma, weights


# ---------------------------------------------------------------
# ---------------------------------------------------------------
