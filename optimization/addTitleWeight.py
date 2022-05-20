import pickle, json
import sqlite3

import sys,re,os,time,operator
import multiprocessing as mp
import mmap
import math
import spacy

def dictInit(list):
    words_dict = {}
    for char in list:
        words_dict[char] = {}
    return words_dict

if __name__=='__main__':
    charlist = [chr(ord('a') + i) for i in range(26)] + ['number']
    print("Index Charlist...", charlist)

    termIdDict = pickle.load(open('termIdDict', 'rb'))
    termIdDictbyChar = dictInit(charlist)

    folder = './text/AA/'
    files= os.listdir(folder)
    for file in files:
        words_dict = pickle.load(open('./text/tmp/' + file[-2:], 'rb'))
        for char in charlist:
            for term, dict in words_dict[char].items():
                pickle.dump(words_dict[char], open('./text/' + char + '/' + file[-2:], 'wb'))


