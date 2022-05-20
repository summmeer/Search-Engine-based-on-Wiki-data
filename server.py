from flask import Flask
import sqlite3
from flask import g
from flask import jsonify
from flask import request
from flask_cors import CORS, cross_origin
# from flask_cache import Cache
from flask_caching import Cache
import json
import random
import time
import difflib
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool

from functools import partial
from numba import jit


from bs4 import BeautifulSoup
import spacy
import re
from nltk.stem.porter import *
import pickle
from searchEngine import searchEngine


# engine = searchEngine()

nlp = spacy.load("en")
stemmer = PorterStemmer()

# termDict = pickle.load(open('./wiki-english/text/termDict', 'rb'))
# charlist = [chr(ord('a') + i) for i in range(26)] + ['number']
# from nltk.stem.wordnet import WordNetLemmatizer
# lmtzr = WordNetLemmatizer()
# stopwords = pickle.load(open('./wiki-english/stoplist', 'rb'))

app = Flask(__name__)
cf = filesystem = {
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 922337203685477580,
    'CACHE_THRESHOLD': 10000
}
cache = Cache(app,config=cf)
DATABASE = 'wsm.db'


def connect_db():
    return sqlite3.connect(DATABASE)

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv


def get_window(searchR, qLemma):
    start = time.time()
    content = searchR['txt']
    title = searchR['title']
    # app.logger.debug(len(content))

    qres = set() #split之后的每个lemma的查找结果
    q_word_res = [] #split之后 然后每个查找结果的单独提取的文字 这是为了加span
    if not content:
        content = title
    # qLemma = list(set([i.lemma_ for i in nlp(query)]))
    t_s = re.split("\s|-", content) #避免 half-blood这种找不到
    res_idx = []
    map_span = {}
    subcontent_interval = 3000
    now_start = 0
    txt_len = len(t_s)
    while not len(res_idx) and now_start<txt_len:
        # sub_t_s = t_s[now_start:now_start+subcontent_interval]
        for qL in qLemma: #query lemma后的每一个词查找相似
            y = set(difflib.get_close_matches(qL,t_s[now_start:now_start+subcontent_interval],100, cutoff=0.6))
            idx = -1
            # app.logger.debug(y)
            for i in y:  
                w = re.compile("[a-z0-9]+", re.I).findall(i) #从查找到的结果中提取单词
                for ww in w:#有可能分离出列表
                    if stemmer.stem(qL) == stemmer.stem(ww): #验证是否是一样的词
                        qres.add(i)
                        tmp = t_s.index(i)
                        if i in map_span:
                            map_span[i] = re.sub(ww, "<span class=\"red\">"+ww+"</span>", map_span[i])
                        else:
                            map_span[i] = re.sub(ww, "<span class=\"red\">"+ww+"</span>", i)
                        if idx==-1 or idx>tmp:
                            idx = tmp
            if idx!=-1:
                res_idx.append(idx)
        maxLen = 45 #单词数
        # app.logger.debug(res_idx)
        now_start += subcontent_interval

    if(len(res_idx)==0):
        ret = content[:250]
    else:
        interval = maxLen//len(res_idx)
        res_idx.sort()
        ret = []
        right = 0
        for idx in res_idx:
            if(idx>right):
                ret.append("...")
                ret.extend(t_s[idx:(idx+interval)])
                right = idx+interval
            else:
                ret.extend(t_s[right:right+interval])
                right += interval
        ret.append("...")
        for i in range(len(ret)):
            if ret[i] in map_span:
                ret[i] = map_span[ret[i]]
        ret = " ".join(ret)
    searchR['window'] = ret
    end = time.time()
    app.logger.debug(end-start)
    app.logger.debug("sub window time")
    return searchR
    

# @cache.memoize(timeout=922337203685477580)
def get_ids_window(ids, query):
    time_s = time.time()
    sql="select id,title,txt,url from original where id in ({seq})".format(
    seq=','.join(['?']*len(ids)))
    res = query_db(sql, ids)
    rl = []
    # query = list(set(engine.wordLemma(query)))
    query = list(set([i.lemma_ for i in nlp(query)]))
    # pool = Pool(len(ids)+1)

    # partial_work = partial(get_window, qLemma=query)
    # rl =pool.map(partial_work, res)
    # pool.close()#关闭进程池，不再接受新的进程
    # pool.join()#主进程阻塞等待子进程的退出
    
    for i in res:
        rl.append(get_window(i, query))
    time_e = time.time()
    app.logger.debug(time_e-time_s)
    app.logger.debug("window time")
    return rl

@app.route('/getPageByIds', methods=["POST"])
@cross_origin()
def get_page():
    data = request.get_data()
    data = json.loads(data)
    ids = data['ids']
    q = data['query']
    r = get_ids_window(ids, q)
    return jsonify(r)

@app.route('/search', methods=["POST"])
@cross_origin()
def search():
    data = request.get_data()
    data = json.loads(data)
    query = data['query'].strip()
    qtype = data['type']
    page_size = data['page_size']
    page = data['page']
    res = {}
    time_start=time.time()
    # query = get_cached_query(query)
    if qtype ==1: #for test
        #ids = [1000, 10000, 10000001, 10000009, 1000001, 10000010, 10000012, 10000017, 1000002, 10000024, 1000003, 10000030, 10000032, 10000034]
        #ids = [31264102, 58716349, 62876298, 31933559, 50630162, 53527843, 23719563, 63201582, 18192773, 55404182, 23421226]
        ids = [727836, 2387806, 3512033, 6548146, 259106, 3997, 55309, 88857]
        #ids = [2270723, 22907207, 17069410]
        #ids = [9316, 39537791, 4273140, 14306242, 1638214, 63325]
        
    if qtype == 2:
        ids = get_bm25_res(query)

    time_end=time.time()
    time_cost = time_end-time_start
    page_ids = ids[(page-1)*page_size:page*page_size]
    r = get_ids_window(page_ids, query)
    res['ids'] = ids
    res['firstPage'] = r
    res['time'] = round(time_cost*1000,4)
    return jsonify(res)


@cache.memoize(timeout=922337203685477580)
def get_bm25_res(query):
    ids = []
    return ids

@cache.memoize(timeout=922337203685477580)
def get_cached_query(query):
    app.logger.debug("##################")
    engine.buildQuery(query)
    return query

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/gtitle/<title>')
def get_content_by_title(title):
    app.logger.debug(title)
    q = "select * from original where title = ?"
    res = query_db(q, [title])
    app.logger.debug(res)
    if len(res):
        return jsonify(res)
    else:
        return 'Hello World!'

@app.route('/getContentById', methods=["GET"])
@cross_origin()
def get_content_by_id():
    aid = request.args.get("id")
    app.logger.debug(aid)
    q = "select * from original where id = ?"
    res = query_db(q, [aid])
    if len(res):
        return jsonify(res)
    else:
        return 'Hello World!'

if __name__ == '__main__':
    app.debug = True
    app.run()