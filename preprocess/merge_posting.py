import pickle, json
import sqlite3

import sys,os,time,operator
import multiprocessing as mp
import mmap
import math
import spacy

def tfNorm():
    docDict = {}
    for char in charlist:
        print("processing...", char)
        for file in files:
            filename = './text/' + char + '/' + file[-2:]
            words_dict = pickle.load(open(filename, 'rb'))
            for term, dict in words_dict.items():
                for doc, num in dict.items():
                    if doc in docDict:
                        docDict[doc] += math.pow(1 + math.log10(num[0]), 2)
                    else:
                        docDict[doc] = math.pow(1 + math.log10(num[0]), 2)
    return docDict

def mergeDict(oriDict, subDict):
    for term, dict in subDict.items():
        if term in oriDict:
            oriDict[term] += [(int(doc), num[0], num[1], math.sqrt(docDict[doc])) for doc, num in dict.items()]
        else:
            oriDict[term] = [(int(doc), num[0], num[1], math.sqrt(docDict[doc])) for doc, num in dict.items()]
    return oriDict

def writePosting(char, oriDict, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        for term, posting in oriDict.items():
            sorted_posting = sorted(posting, key=operator.itemgetter(1), reverse=True)
            encode_posting = json.dumps(sorted_posting)
            pos = f.tell()
            f.write(encode_posting)
            f.write('\n')
            t = (term, encode_posting)
            c.execute("INSERT INTO posting VALUES (?, ?)", t)
            wholeDict[char][term] = (len(sorted_posting), pos)

def loadFile(filename):
    return pickle.load(open(filename, 'rb'))

def writeFile(dict, filename):
    pickle.dump(dict, open(filename, 'wb'))

def memory_map(filename, access=mmap.ACCESS_WRITE):
    size = os.path.getsize(filename)
    fd = os.open(filename, os.O_RDWR)
    return mmap.mmap(fd, size, access=access)

def dictInit(list):
    words_dict = {}
    for char in list:
        words_dict[char] = {}
    return words_dict

if __name__=='__main__':
    charlist = [chr(ord('a') + i) for i in range(26)] + ['number']
    print("Index Charlist...", charlist)

    db_path = 'wsm.db'
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''DROP TABLE IF EXISTS posting''')
    c.execute('''CREATE TABLE posting
                (term TEXT PRIMARY KEY, postings TEXT)''')

    folder = './text/AA/'
    files= os.listdir(folder)
    wholeDict = dictInit(charlist)
    print("compute tfNorm")
    docDict = tfNorm()

    termIdDict = pickle.load(open('termIdDict', 'rb'))

    for char in charlist:
        print("processing...", char)
        start_time = time.time()
        oriDict = {}
        for file in files:
            filename = './text/' + char + '/' + file[-2:]
            subDict = loadFile(filename)
            oriDict = mergeDict(oriDict, subDict)
        print ("counting...", len(oriDict))
        print ("writing posting...")
        writePosting(char, oriDict, './text/' + char + '/posting')
        print ("time...", time.time() - start_time)
    print ("total terms...", sum([len(wholeDict[i]) for i in charlist]))
    conn.commit()
    conn.close()
    # save term dict
    writeFile(wholeDict, './text/termDict')
