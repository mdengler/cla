#!/usr/bin/env python
# On 20130210, v0.2
# Critical Line Algorithm Snippet 16. Using the CLA class.
# by MLdP <lopezdeprado@lbl.gov>
#
# From: http://papers.ssrn.com/sol3/papers.cfm?abstract_id=2197616
#
# "All code in this paper is provided 'as is', and contributed to the
# academic community for non-business purposes only, under a GNU-GPL
# license"
#

def plot2D(x, y, xLabel = '', yLabel = '', title = '', pathChart = None):
    import matplotlib.pyplot as mpl
    fig = mpl.figure()
    ax = fig.add_subplot(1, 1, 1) # one row, one column, first plot
    ax.plot(x, y, color = 'blue')
    ax.set_xlabel(xLabel)
    ax.set_ylabel(yLabel, rotation = 90)
    mpl.xticks(rotation = 'vertical')
    mpl.title(title)
    if pathChart == None:
        mpl.show()
    else:
        mpl.savefig(pathChart)
        mpl.clf() # reset pylab
    return

def main():
    import numpy as np
    import CLA
    #1) Path
    path='H:/PROJECTS/Data/CLA_Data.csv'
    #2) Load data, set seed
    headers=open(path,'r').readline().split(',')[:-1]
    data=np.genfromtxt(path,delimiter=',',skip_header=1) # load as numpy array
    mean=np.array(data[:1]).T
    lB=np.array(data[1:2]).T
    uB=np.array(data[2:3]).T
    covar=np.array(data[3:])
    #3) Invoke object
    cla=CLA.CLA(mean,covar,lB,uB)
    cla.solve()
    print cla.w # print all turning points
    #4) Plot frontier
    mu,sigma,weights=cla.efFrontier(100)
    plot2D(sigma, mu, 'Risk', 'Expected Excess Return', 'CLA-derived Efficient Frontier')
    #5) Get Maximum Sharpe ratio portfolio
    sr,w_sr = cla.getMaxSR()
    print np.dot(np.dot(w_sr.T, cla.covar), w_sr)[0, 0]**.5, sr
    print w_sr
    #6) Get Minimum Variance portfolio
    mv, w_mv = cla.getMinVar()
    print mv
    print w_mv
    return
#---------------------------------------------------------------
# Boilerplate
if __name__ == '__main__':main()
