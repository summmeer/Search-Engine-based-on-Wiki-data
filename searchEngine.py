import json, pickle
import sys, os, re, time, nltk
from nltk.stem.wordnet import WordNetLemmatizer
import mmap
import logging
from score import Score
import spacy
import sqlite3
import ujson

class searchEngine():
    def __init__(self):
        self.termDict = pickle.load(open('./wiki-english/text/termDict', 'rb'))
        self.charlist = [chr(ord('a') + i) for i in range(26)] + ['number']
        self.lmtzr = WordNetLemmatizer()
        self.stopwords = pickle.load(open('./wiki-english/stoplist', 'rb'))
        self.lemmaQuery = []
        self.query = ""
        self.queryDict = self.__dictInit()
        self.nlp = spacy.load('en_core_web_sm')
        self.PRDict = pickle.load(open('PRDict', 'rb'))
        
    def __clean_page(self, text_page):
        # leave a-z and '
        pat_letter = re.compile(r'[^a-zA-Z0-9 \']+')
        # abbr
        pat_is = re.compile("(it|he|she|that|this|there|here)(\'s)", re.I)
        pat_s = re.compile("(?<=[a-zA-Z])\'s") # 's
        pat_s2 = re.compile("(?<=s)\'s?")
        pat_not = re.compile("(?<=[a-zA-Z])n\'t") # not
        pat_would = re.compile("(?<=[a-zA-Z])\'d") # would
        pat_will = re.compile("(?<=[a-zA-Z])\'ll") # will
        pat_am = re.compile("(?<=[I|i])\'m") # am
        pat_are = re.compile("(?<=[a-zA-Z])\'re") # are
        pat_ve = re.compile("(?<=[a-zA-Z])\'ve") # have

        new_text = pat_letter.sub(' ', text_page).strip().lower()
        new_text = pat_is.sub(r"\1 is", new_text)
        new_text = pat_s.sub("", new_text)
        new_text = pat_s2.sub("", new_text)
        new_text = pat_not.sub(" not", new_text)
        new_text = pat_would.sub(" would", new_text)
        new_text = pat_will.sub(" will", new_text)
        new_text = pat_am.sub(" am", new_text)
        new_text = pat_are.sub(" are", new_text)
        new_text = pat_ve.sub(" have", new_text)
        new_text = new_text.replace('\'', ' ')
        return new_text

    # get pos via tag
    def __get_wordnet_pos(self, treebank_tag):
        if treebank_tag.startswith('J'):
            return nltk.corpus.wordnet.ADJ
        elif treebank_tag.startswith('V'):
            return nltk.corpus.wordnet.VERB
        elif treebank_tag.startswith('N'):
            return nltk.corpus.wordnet.NOUN
        elif treebank_tag.startswith('R'):
            return nltk.corpus.wordnet.ADV
        else:
            return ''

    def __dictInit(self):
        queryDict = {}
        for char in self.charlist:
            queryDict[char] = {}
        return queryDict

    def lemma(self, word):
        if word and word not in self.stopwords:
            tag = nltk.pos_tag(word) # tag is like [('bigger', 'JJR')]
            pos = self.__get_wordnet_pos(tag[0][1])
            if pos:
                lemmatized_word = self.lmtzr.lemmatize(word, pos)
                return lemmatized_word
            else:
                return word

    def wordLemma(self, words):
        # new_words = self.pool.map(self.lemma, words)
        doc = self.nlp(words)
        new_words = [token.lemma_ for token in doc]
        return new_words

    def pageLemma(self, page):
        cleanpage = self.__clean_page(page).split()
        lemmawords = self.wordLemma(cleanpage)
        result = []
        for word in lemmawords:
            if word:
                result.append(word)
        return result

    def parseQuery(self):
        # time1 = time.time()
        cleanquery = self.__clean_page(self.query)
        # time2 = time.time()
        # print("clean query time...", time2-time1)
        lemmawords = self.wordLemma(cleanquery)
        # time3 = time.time()
        # print("lemma time...", time3-time2)
        self.lemmaQuery = []
        self.queryDict = self.__dictInit()
        for word in lemmawords:
            if word and word not in self.stopwords:
                self.lemmaQuery.append(word)
        for lemmaq in self.lemmaQuery:
            first_ch = lemmaq[0]
            if first_ch not in self.charlist[:-1]:
                first_ch = 'number'
            if lemmaq in self.queryDict[first_ch]:
                self.queryDict[first_ch][lemmaq] += 1
            else:
                self.queryDict[first_ch][lemmaq] = 1

    def __memory_map(self, filename, access=mmap.ACCESS_WRITE):
        size = os.path.getsize(filename)
        fd = os.open(filename, os.O_RDWR)
        return fd, mmap.mmap(fd, size, access=access)
    
    def loadPosting(self):
        postingLists = []
        termLists = []
        for first_ch, termsDict in self.queryDict.items():
            if len(termsDict)>0:
                fd, m = self.__memory_map('./wiki-english/text/' + first_ch + '/posting')
                for term, fq in termsDict.items():
                    if term in self.termDict[first_ch]:
                        (df, pos) = self.termDict[first_ch][term]
                        termLists.append([fq, df])
                        m.seek(pos)
                        posting = m.readline()
                        posting = json.loads(posting)
                        postingLists.append(posting)
                    else:
                        logging.info("In query:" + self.query + ", term " + term + " not in termDict.")
                m.close()
                os.close(fd)
        return termLists, postingLists

    def loadPostingDb(self):
        db_path = 'wsm.db'
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        postingLists = []
        termLists = []
        for first_ch, termsDict in self.queryDict.items():
            if len(termsDict)>0:
                for term, fq in termsDict.items():
                    if term in self.termDict[first_ch]:
                        (df, pos) = self.termDict[first_ch][term]
                        termLists.append([fq, df])
                        cursor = c.execute("SELECT postings from posting where term=\"" + term + "\";")
                        #start = time.time()
                        for r in cursor:
                            #print(sys.getsizeof(r[0]))
                            posting = ujson.loads(r[0])
                            #print("json load time", time.time()-start)
                            size = len(posting)
                            postingLists.append(posting[:size//3])
                    else:
                        logging.info("In query:" + self.query + ", term " + term + " not in termDict.")
        conn.close()
        return termLists, postingLists

    def buildQuery(self, query):
        self.query = query
        # start = time.time()
        self.parseQuery()
        # print("parseQuery time...", time.time()-start)
        # start = time.time()
        #termLists, postingLists = self.loadPosting()
        termLists, postingLists = self.loadPostingDb()
        # print("load posting time...", time.time()-start)
        # compute score
        self.computeScore = Score(termLists, postingLists, self.PRDict)
    
    def searchByMethod(self, method):
        if method == "jaccard":
            return self.computeScore.jaccard()
        if method == "tf_simi":
            return self.computeScore.tf_simi()
        if method == "tf_idf":
            return self.computeScore.tf_idf()
        if method == "bm25":
            return self.computeScore.bm25()
        if method == "betterTfIdf":
            return self.computeScore.betterTfIdf()

if __name__=='__main__':
    start = time.time()
    engine = searchEngine()
    print("Init time...", time.time()-start)
    query = "Harry Potter and Half-Blood Prince"
    start = time.time()
    engine.buildQuery(query)
    print("buildQuery time...", time.time()-start)
    print("queryDict...", engine.queryDict)
    print("=====search jaccard=====")
    start = time.time()
    resultList = engine.searchByMethod("jaccard")
    print("Search time...", time.time()-start)
    print("Len of result ", len(resultList))
    print("result example ", resultList[:10])

    print("=====search tf simi=====")
    start = time.time()
    resultList = engine.searchByMethod("tf_simi")
    print("Search time...", time.time()-start)
    print("Len of result ", len(resultList))
    print("result example ", resultList[:10])

    print("=====search tf idf=====")
    start = time.time()
    resultList = engine.searchByMethod("tf_idf")
    print("Search time...", time.time()-start)
    print("Len of result ", len(resultList))
    print("result example ", resultList[:10])

    print("=====bm25=====")
    start = time.time()
    resultList = engine.searchByMethod("bm25")
    print("Search time...", time.time()-start)
    print("Len of result ", len(resultList))
    print("result example ", resultList[:10])

    print("=======change query=======")
    query = "Geoffrey Hinton"
    engine.buildQuery(query)
    resultList = engine.searchByMethod("betterTfIdf")
    print("result example ", resultList[:10])
