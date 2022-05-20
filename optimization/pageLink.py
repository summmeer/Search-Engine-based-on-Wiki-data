import pickle, json
import sqlite3

import sys,re,os,time,operator
import multiprocessing as mp
import mmap
import math
from urllib.parse import unquote
from bs4 import BeautifulSoup

def processPage():
    pageLinkDict = {}
    cursor = c.execute('''SELECT id, content from original;''')
    cnt = 0
    hit = 0
    miss = 0
    for row in cursor:
        #print(content)
        cnt += 1
        if cnt%100000:
            print("processing...", cnt)
        start = time.time()
        soup = BeautifulSoup(row[1], 'html.parser')
        pageLinkDict[int(row[0])] = []
        for link in soup.find_all('a'):
            title = unquote(link['href'])
            if title in titleIdDict:
                pageLinkDict[int(row[0])].append(int(titleIdDict[title]))
                hit += 1
            else:
                #print(title)
                miss += 1
        print(time.time()-start)
        break
    pickle.dump(pageLinkDict, open('pageLinkDict', 'wb'))
    print("hit num...", hit)
    print("miss num...", miss)


if __name__=='__main__':
    db_path = 'wsm.db'
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    titleIdDict = pickle.load(open('titleIdDict', 'rb'))
    processPage()
    conn.commit()
    conn.close()
