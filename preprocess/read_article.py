import json, pickle

import sys,os,re,time,nltk
import multiprocessing as mp
from nltk.stem.wordnet import WordNetLemmatizer

def cleanPage(text_page):
    pat_link1 = re.compile("<a href[^>]*>")
    pat_link2 = re.compile("</a>")
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

    new_text = pat_link1.sub("", text_page)
    new_text = pat_link2.sub("", new_text)
    new_text = pat_letter.sub(' ', new_text).strip().lower()
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
def get_wordnet_pos(treebank_tag):
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

def lemma(word):
    if word and word not in stopwords:
        tag = nltk.pos_tag(word) # tag is like [('bigger', 'JJR')]
        pos = get_wordnet_pos(tag[0][1])
        if pos:
            lemmatized_word = lmtzr.lemmatize(word, pos)
            return lemmatized_word
        else:
            return word

def wordLemma(words):
    new_words = pool.map(lemma, words)
    return new_words

def getWordsDict(text_page, docid, freq):
    # time1 = time.time()
    words = cleanPage(text_page).split()
    # time2 = time.time()
    # print("clean time...", time2-time1)
    lemmaWords = wordLemma(words)
    # time3 = time.time()
    # print("lemma time...", time3-time2)
    for lemma_word in lemmaWords:
        if not lemma_word:
            continue
        first_ch = lemma_word[0]
        if first_ch not in charlist[:-1]:
            first_ch = 'number'
        if lemma_word in words_dict[first_ch]:
            if docid in words_dict[first_ch][lemma_word]:
                words_dict[first_ch][lemma_word][docid][0] += 1
            else:
                words_dict[first_ch][lemma_word][docid] = (freq, len(lemmaWords))
        else:
            words_dict[first_ch][lemma_word] = {}
            words_dict[first_ch][lemma_word][docid] = (freq, len(lemmaWords))
    # time4 = time.time()
    # print("hash time...", time4-time3)

def writeFile(dict, filename):
    pickle.dump(dict, open(filename, 'wb'))

def dictInit(list):
    words_dict = {}
    for char in list:
        words_dict[char] = {}
    return words_dict

if __name__=='__main__':
    lmtzr = WordNetLemmatizer()
    stopwords = pickle.load(open('stoplist', 'rb'))
    charlist = [chr(ord('a') + i) for i in range(26)] + ['number']
    print("Index Charlist...", charlist)

    folder = './text/AA/'
    files= os.listdir(folder)
    pool = mp.Pool()
    for file in files:
        filename = os.path.join(folder, file)
        print("processing...", filename)
        start_time = time.time()
        input_file = open(filename, 'r')
        words_dict = dictInit(charlist)
        while True:
            line = input_file.readline()
            if not line:
                break
            line = json.loads(line)
            getWordsDict(line['text'], line['id'], 1)
            break
        input_file.close()

        print ("counting...", sum([len(words_dict[i]) for i in charlist]))
        print ("time...", time.time() - start_time)
        print ("writing file...")
        print (words_dict['number'])
        for char in charlist:
            writeFile(words_dict, './text/' + char + '/' + file[-2:])
