import time
import math

class Score(object):
    def __init__(self, termLists, postingLists, PRdict):
        self.__parse_posting(postingLists)
        self.termfq = [l[0] for l in termLists]
        self.termdf = [l[1] for l in termLists]
        self.PRdict = PRdict
        self.documentN = 6091006.0
        self.avgLen = 359.92
        
    def __parse_posting(self, postingLists):
        self.docIdList = []
        self.docLenList = []
        self.docTfList = []
        self.docTfNormList = []
        for postingList in postingLists:
            self.docIdList.append([l[0] for l in postingList])
            self.docLenList.append([l[2] for l in postingList])
            self.docTfList.append([l[1] for l in postingList])
            self.docTfNormList.append([l[3] for l in postingList])

    def jaccard(self):
        scoreDict = {}
        time1 = time.time()
        for index, tfq in enumerate(self.termfq):
            for idx, docid in enumerate(self.docIdList[index]):
                score = float(tfq)/math.sqrt(self.docLenList[index][idx])
                if docid in scoreDict:
                    scoreDict[docid] += score
                else:
                    scoreDict[docid] = score
        # print(scoreDict)
        time2 = time.time()
        print("build dict time...", time2-time1)
        sortid = sorted(scoreDict.items(), key=lambda item: item[1], reverse=True)
        # print(sortid)
        time3 = time.time() 
        print("sort score time...", time3-time2)
        sortid = [id[0] for id in sortid[:len(sortid)//2]]
        return sortid

    def tf_simi(self):
        scoreDict = {}
        termLen = sum(self.termfq)
        time1 = time.time()
        for index, tfq in enumerate(self.termfq):
            for idx, docid in enumerate(self.docIdList[index]):
                score = float(tfq * self.docTfList[index][idx]) / math.sqrt(termLen * self.docLenList[index][idx])
                if docid in scoreDict:
                    scoreDict[docid] += score
                else:
                    scoreDict[docid] = score
        # print(scoreDict)
        time2 = time.time()
        print("build dict time...", time2-time1)
        sortid = sorted(scoreDict.items(), key=lambda item: item[1], reverse=True)
        # print(sortid)
        time3 = time.time() 
        print("sort score time...", time3-time2)
        sortid = [id[0] for id in sortid[:len(sortid)//2]]
        return sortid

    def tf_idf(self): # lnc.ltc
        scoreDict = {}
        time1 = time.time()
        termLen = sum(self.termfq)
        for index, tfq in enumerate(self.termfq):
            term_ltc = (1 + math.log10(tfq)) * math.log10(self.documentN / self.termdf[index])
            for idx, docid in enumerate(self.docIdList[index]):
                doc_lnc = term_ltc * (1 + math.log10(self.docTfList[index][idx])) / self.docTfNormList[index][idx]
                if docid in scoreDict:
                    scoreDict[docid] += doc_lnc
                else:
                    scoreDict[docid] = doc_lnc
        # print(scoreDict)
        time2 = time.time()
        print("build dict time...", time2-time1)
        sortid = sorted(scoreDict.items(), key=lambda item: item[1], reverse=True)
        # print(sortid)
        time3 = time.time() 
        print("sort score time...", time3-time2)
        sortid = [id[0] for id in sortid[:len(sortid)//2]]
        return sortid

    def bm25(self):
        scoreDict = {}
        time1 = time.time()
        k1 = 3.0
        b = 0.75
        for index, tfq in enumerate(self.termfq):
            term_w = (2 * tfq / (1.0 + tfq)) * math.log2((self.documentN - self.termdf[index] + 0.5 )/ (self.termdf[index] + 0.5))
            for idx, docid in enumerate(self.docIdList[index]):
                doc_w = term_w * (k1 + 1) * self.docTfList[index][idx] / (self.docTfList[index][idx] + k1 * (1 - b + b * self.docLenList[index][idx]/self.avgLen))
                if docid in scoreDict:
                    scoreDict[docid] += doc_w
                else:
                    scoreDict[docid] = doc_w
        # print(scoreDict)
        time2 = time.time()
        print("build dict time...", time2-time1)
        sortid = sorted(scoreDict.items(), key=lambda item: item[1], reverse=True)
        # print(sortid)
        time3 = time.time() 
        print("sort score time...", time3-time2)
        sortid = [id[0] for id in sortid[:len(sortid)//2]]
        return sortid

    def betterTfIdf(self):
        scoreDict = {}
        time1 = time.time()
        termLen = sum(self.termfq)
        for index, tfq in enumerate(self.termfq):
            term_ltc = (1 + math.log10(tfq)) * (math.log10(self.documentN / self.termdf[index]) ** 2)
            for idx, docid in enumerate(self.docIdList[index]):
                doc_lnc = term_ltc * (1 + math.log10(self.docTfList[index][idx])) / self.docTfNormList[index][idx]
                if docid in scoreDict:
                    scoreDict[docid][0] += doc_lnc
                    scoreDict[docid][1] += tfq
                else:
                    scoreDict[docid] = [doc_lnc, tfq]
        # print(scoreDict)
        time2 = time.time()
        print("build dict time...", time2-time1)
        for docid, score in scoreDict.items():
            scoreDict[docid] = score[0] * (float(score[1]) / termLen)**2 * math.log2(self.PRdict[docid])
        sortid = sorted(scoreDict.items(), key=lambda item: item[1], reverse=True)
        # print(sortid)
        time3 = time.time() 
        print("sort score time...", time3-time2)
        sortid = [id[0] for id in sortid[:len(sortid)//2]]
        return sortid

if __name__=='__main__':
    # term1: 1-2-3-4-10
    # term2: 2-3-10
    # term3: 3-10
    # term3: 3-10
    termLists = [[1, 1000], [1, 2000], [2, 1500]]
    postingLists = [[[1, 100, 200, 20], [2, 50, 150, 40], [3, 100, 200, 10], [4, 50, 150, 5], [10, 100, 200, 20]], 
                    [[2, 10, 150, 40], [3, 30, 200, 10], [10, 50, 200, 20]], 
                    [[3, 80, 200, 10], [10, 80, 200, 20]]]
    computeScore = Score(termLists, postingLists)
    print(computeScore.termfq)
    print(computeScore.docIdList)
    print(computeScore.docLenList)
    print(computeScore.docTfList)
    print("===jaccard===")
    docid = computeScore.jaccard()
    print(docid)
    print("===tf_simi===")
    docid = computeScore.tf_simi()
    print(docid)
    print("===tf_idf===")
    docid = computeScore.tf_idf()
    print(docid)
    print("===bm25===")
    docid = computeScore.bm25()
    print(docid)
    print("===betterTfIdf===")
    docid = computeScore.betterTfIdf()
    print(docid)
