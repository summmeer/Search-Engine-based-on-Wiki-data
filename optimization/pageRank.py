import pickle, json
import sqlite3

import sys,re,os,time,operator
import multiprocessing as mp
import mmap
import math

import numpy as np
from scipy.sparse import csc_matrix

def pageRank(G, d=.85, maxerr=.0001):
    """
    Computes the pagerank for each of the n states Parameters
    ----------
    G: matrix representing state transitions
    Gij is a binary value representing a transition from state i to j.
    d: probability of following a transition. 1-d probability of teleporting to another state.
    maxerr: if the sum of pageranks between iterations is bellow this we will have converged.
    """
    n = len(G)
    ro, r = np.zeros(n), np.ones(n)
    while np.sum(np.abs(r - ro)) > maxerr:
        ro = r.copy()
        for i in range(0, n):
            pr = 0
            for l in G[i]:
                pr += r[l] / float(lenDict[l])
            r[i] = pr * d + (1 - d) / float(n)
    return r / float(sum(r))

def mapPage():
    idDict = {}
    lenDict = {}
    cnt = 0
    print("mapping...")
    for pid, links in pageLinkDict.items():
        idDict[pid] = cnt
        lenDict[cnt] = len(links)
        cnt += 1
    print("Construct G...")
    Glist = [[] for i in range(cnt)]
    # print(Glist)
    for pid, links in pageLinkDict.items():
        for l in links:
            if l in idDict:
                Glist[idDict[l]].append(idDict[pid])
    print("len of G...", len(Glist))
    return Glist, idDict, lenDict

def getRealPR(ranklist, idDict):
    PRDict = {}
    for pid, cnt in idDict.items():
        PRDict[pid] = ranklist[cnt]
    return PRDict

if __name__=='__main__':
    pageLinkDict = pickle.load(open('pageLinkDict', 'rb'))
    # pageLinkDict = {'A':['B', 'C', 'E'], 'B': ['C'], 'C': ['A', 'E'], 'D': ['A'], 'E': ['A']}
    G, idDict, lenDict = mapPage()
    ranklist = pageRank(G, d=0.85)
    PRDict = getRealPR(ranklist, idDict)
    pickle.dump(PRDict, open('PRDict', 'wb'))
    # print(PRDict)
