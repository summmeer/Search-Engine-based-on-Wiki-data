# Search-Engine-based-on-Wiki-data
Wikipedia is a well-known free online encyclopedia, created and edited by volunteers around the world, and it offers free copies of all available content, where we can get the latest complete dump of the English-language Wikipedia. Thus, we build a Wikipedia-based search engine: Wing, with 5 sort algorithms, a well-designed GUI, and the responsive time scale of millisecond. Wing is short for ``Wing Is Not Google''.

![image](https://github.com/summmeer/Search-Engine-based-on-Wiki-data/blob/main/fig/system.svg)
*The overflow of search engine WING*

## Backend: search engine

### Build postings
After we download the 17GB zip file of the whole raw data and unzip it, we use a Wiki-Extractor tool [WikiExtractor.py](http://medialab.di.unipi.it/wiki/Wikipedia_Extractor) to extract around 10 million documents. 

Data Source (Choose one): [Wikipedia in English](https://dumps.wikimedia.org/enwiki/latest/) and [Wikipedia in Chinese](https://dumps.wikimedia.org/zhwiki/latest/).

After removing templates, undesired xml namespaces, and disambiguation pages, we leave around 6 million documents in database and each documents contains an ```id```, a ```title```, and the text with ```<a> </a>``` tag in HTML format. These documents are extracted in 17 block files.

``` bash
cd preprocess
python read_article.py
python merge_posting.py
```
We use SPIMI (Single-Pass In-Memory Indexing) algorithm to construct posting list.

![image](https://github.com/summmeer/Search-Engine-based-on-Wiki-data/blob/main/fig/posting.svg)
*The overflow of postings building*

### Sort algorithms
We use: Jaccard, TF-simi, TF-IDF, BM25, Better TF-IDF with Page Rank. The implementation is in ```score.py```. 

## Backend: API
We adopt Flask to enable our back end. Flask is a microframework for web appliction written in Python. The base address of the back end is ```http://localhost:5000```. Run server:
``` bash
python server.py
```

## Frontend (GUI)
Front end is implemented with Vue. Vue is a progressive framework for building user interfaces. Also, we use Element UI, a desktop component library, to make our interface more beautiful and user-friendly. Front end includes three pages: welcome page, query page, and article page.

![image](https://github.com/summmeer/Search-Engine-based-on-Wiki-data/blob/main/fig/welcome.png)
*Welcome page of the front end*

![image](https://github.com/summmeer/Search-Engine-based-on-Wiki-data/blob/main/fig/search.png)
*Query page of the front end*

This part is implemented by [@Polynomia](https://github.com/Polynomia)

Build Setup:

``` bash
cd frontend

# install dependencies
npm install

# serve with hot reload at localhost:8080
npm run dev

# build for production with minification
npm run build

# build for production and view the bundle analyzer report
npm run build --report
```

For a detailed explanation on how things work, check out the [guide](http://vuejs-templates.github.io/webpack/) and [docs for vue-loader](http://vuejs.github.io/vue-loader).

## Optimize
- TF-IDF based methods will give short articles high weights. So, there will be a problem that some docs that their content is very short but not very relative to the query, have high weights in ranking results. Thus, when we calculate the term frequency, we increase the term frequency of the words that appear in the title. Through this way, we can filter some short but meaning less docs and get what we want.

- It is well known that Python program is running as a single process and is very slow. To speed up our program written by Python, we use ```Multiprocess``` package to accelerate our for-loop.