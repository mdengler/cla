#!/usr/bin/env python
#
# I (Martin Dengler) have been given the OK to upload this code to
# github, as long as I indicate:
#
# 1.  That David H. Bailey and Marcos Lopez de Prado are the original
#     authors.
#
# 2.  That this code is provided under a GPL license for
#     non-commercial purposes.
#
# 3.  That the original authors retain the rights as it relates to
#     commercial applications.
#
# The accompanying paper was published in an open-access application:
# http://ssrn.com/abstract=2197616
#
# The original code is here:
#
# http://www.quantresearch.info/CLA.py.txt
# http://www.quantresearch.info/CLA_Main.py.txt
#
# A sample dataset can be found here:
# http://www.quantresearch.info/CLA_Data.csv.txt
#
#
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

import os
import urllib2


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

def main(args):
    import numpy as np
    import CLA
    #1) Path
    path=args[0]
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
if __name__ == '__main__':
    import sys
    args = sys.argv[1:]
    if len(args) < 1:
        args.append("data.csv")
        if not os.path.exists("data.csv"):
            url = "http://www.quantresearch.info/CLA_Data.csv.txt"
            open("data.csv", "w").write(urllib2.urlopen(url).read())
    main(args)
