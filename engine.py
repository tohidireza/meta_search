import argparse
from collections import Counter
from thread import start_new_thread
import timeit
from bs4 import BeautifulSoup
import urllib, urllib2
import json
from nltk.tokenize import word_tokenize
import matplotlib.pyplot as plt
import bs4 as bs
import math
import time

num_threads = 0
with open('cache.json', 'r') as jfile:
    cache = json.load(jfile)

global cl
cl = 0


def search_parsijoo(query):
    address = "http://parsijoo.ir/web?q=" + urllib.quote_plus(query) + "&period=all&filetype=any&site="
    request = urllib2.Request(address, None, {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 '
                      'Safari/537.36'})
    urlfile = urllib2.urlopen(request)
    page = urlfile.read()
    soup = BeautifulSoup(page, "html.parser")
    result_url = soup.findAll('span', attrs={'class': 'result-url'})
    # result_title = soup.findAll('span', attrs={'class': 'result-title'})
    # result_desc = soup.findAll('span', attrs={'class': 'result-desc'})
    # pprint(results)
    i = 0
    # for result in results:
    #     print(
    #         "---------------------------------------------------------------------------------------------"
    #         "----------------------")
    #     # header.a.string.encode('utf-8')
    #     # k = header.a.get('href')
    #     # u = k.decode('utf-8')
    #     # u = u.rstrip('/')
    #     print(result_title[i].text.encode('utf-8'))
    #     # print(result.text.encode('utf-8'))
    #     # print(result_desc[i].text.encode('utf-8'))
    #     i += 1

    return result_url


def search_yooz(query):
    address = "https://yooz.ir/search/?q=" + urllib.quote_plus(query)
    request = urllib2.Request(address, None,
                              {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0"})
    urlfile = urllib2.urlopen(request)
    page = urlfile.read()
    soup = BeautifulSoup(page, "html.parser")

    result_url = soup.findAll('span', attrs={'class': 'result-meta result__url'})
    # result_title = soup.findAll('a', attrs={'class': 'resault__title__a'})
    # result_desc = soup.findAll('div', attrs={'class': 'result__row result-body'})
    # pprint(results)
    # i = 0
    # for result in results:
    #     print(
    #         "--------------------------------------------------------------------------------------------"
    #         "-----------------------")
    #     # header.a.string.encode('utf-8')
    #     # k = header.a.get('href')
    #     # u = k.decode('utf-8')
    #     # u = u.rstrip('/')
    #     print(result_title[i].text.encode('utf-8'))
    #     # print(result.text.encode('utf-8'))
    #     # print(result_desc[i].text.encode('utf-8'))
    #     i += 1

    return result_url


def tf_idf(query, search_results):
    start = time.time()
    # TOKENINZING QUERRY
    Qtoken = word_tokenize(query);
    QUERRY = {}
    RANK_INDEX = {}
    for key in Qtoken:
        QUERRY[key] = {}
    DOCID = {}  # DOCUMENT ID MAPPING OF ALL URLS
    d = 0
    for apage in search_results:
        RANK_INDEX[apage] = {}
    # TERM FREQUENCY CALCULATION
    i = 1
    for apage in search_results:
        # print apage+"ojasvi"
        try:
            sauce = urllib.urlopen(apage).read()
            soup = bs.BeautifulSoup(sauce, 'lxml')
            data = soup
            document = ''
            for text in data.findAll('p'):
                document += text.getText()
            DOCTERM = word_tokenize(document)
            for term in Qtoken:
                freq = 0
                if term in DOCTERM:
                    freq = DOCTERM.count(term)
                    QUERRY[term][apage] = math.log10(freq) + 1
                    RANK_INDEX[apage][term] = math.log10(freq) + 1
                else:
                    QUERRY[term][apage] = 1
                    RANK_INDEX[apage][term] = 1
        except:
            # print 'Exception'
            for term in Qtoken:
                QUERRY[term][apage] = 1
                RANK_INDEX[apage][term] = 1
        print("******************************************************************", i)
        i += 1
    end = time.time()
    # IDF CALCULATION
    # print QUERRY
    IDF = {}
    for terms in QUERRY:
        ids = math.log10(float(len(search_results)) / float(len(QUERRY[terms])))
        if (ids == 0):
            ids = 1
        IDF[terms] = ids
    # print RANK_INDEX
    Rank = []
    for links in RANK_INDEX:
        link_scr = 0
        if (len(RANK_INDEX[links]) > 0):
            for terms in RANK_INDEX[links]:
                # print terms+"  ,  "+links
                tf = QUERRY[terms][links]
                idf = IDF[terms]
                link_scr += tf * idf
        lists = [links, link_scr]
        Rank.append(lists)

    for website in Rank:
        try:
            wot_sc = web_of_trust(website[0])
        except:
            wot_sc = 0
        ind = Rank.index(website)
        website[1] = website[1] + wot_sc
        Rank[ind] = website

    Rank.sort(key=lambda x: x[1])
    rlen = len(Rank)
    global final_link_results
    while (rlen > -1):
        print Rank[rlen - 1]
        final_link_results.append(Rank[rlen - 1])
        rlen = rlen - 1
    # print "time taken: ",end-start
    global cl
    cl = 1


def web_of_trust(website):
    url = None
    if '.com' in website:
        ind = website.index('.com')
        url = 'http://api.mywot.com/0.4/public_link_json2?hosts=' + website[
                                                                    :ind + 4] + '/&callback=process&key=f2611810521b7bb56215f0b2cacbd905257d7aa8'
    elif '.in' in website:
        ind = website.index('.in')
        url = 'http://api.mywot.com/0.4/public_link_json2?hosts=' + website[
                                                                    :ind + 3] + '/&callback=process&key=f2611810521b7bb56215f0b2cacbd905257d7aa8'
    elif '.gov' in website:
        ind = website.index('.gov')
        url = 'http://api.mywot.com/0.4/public_link_json2?hosts=' + website[
                                                                    :ind + 4] + '/&callback=process&key=f2611810521b7bb56215f0b2cacbd905257d7aa8'
    else:
        url = 'http://api.mywot.com/0.4/public_link_json2?hosts=' + website + '/&callback=process&key=f2611810521b7bb56215f0b2cacbd905257d7aa8'
    wot_score = 0
    print "website is " + str(website)
    response = urllib2.urlopen(url).read()
    # print " ** WEB of TRUST Results ** "
    # print response[8:-1]
    resp_dict = json.loads(response[8:-1])
    # print resp_dict
    for key in resp_dict:
        if (resp_dict[key].get('0')):
            score = resp_dict[key]['0']
            wot_score = float(float(score[0]) * float(score[1]) / float(1000))
        # print resp_dict[key]['0']
    # print " Website score is : " + str(wot_score)
    return wot_score


def analysis(clen, all_len):
    labels = 'Common Links', 'Uncommon Links'
    sizes = []
    sizes.append(clen)
    sizes.append(all_len - clen)
    colors = ['gold', 'lightcoral']
    explode = (0.1, 0,)
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
    plt.axis('equal')
    plt.show()


def main():
    parser = argparse.ArgumentParser(description='Naser Meta Search Engine', add_help=True)

    parser.add_argument('-q', action='store', dest='query',
                        help='Query that will be searched!')

    args = parser.parse_args()
    query = args.query

    if not query:
        print 'Search query not entered!'
        parser.print_usage()
    else:

        for key in cache:
            if (key == query):
                print "\n###  Query fetched from cache ###### \n"
                post = cache[key]
                for num in range(0, len(post)):
                    print post[num]
                exit()
        print "\nQuery not present in cache ......... \n"
        st = timeit.default_timer()

        parsi_result_url = search_parsijoo(query)
        yooz_result_url = search_yooz(query)

        # merge results urls
        urls = parsi_result_url + yooz_result_url
        # strip spaces, tabs and newlines
        all_links = [' '.join(url.text.encode('utf-8').split()) for url in urls]

        cnt = Counter(all_links)
        common_links = [k for k, v in cnt.iteritems() if v > 1]

        uncommon_links = list(set(all_links) - set(common_links))
        #
        print "\n\n ** Common links ** \n"
        for element in common_links:
            print element
        print "\n\n ** Uncommon links ** \n "
        for element in uncommon_links:
            print element
        #
        global final_link_results
        final_link_results = []
        start_new_thread(tf_idf, (query, common_links,))
        global cl
        while cl != 1:
            pass
        cl = 0
        final_link_results.pop()
        start_new_thread(tf_idf, (query, uncommon_links,))
        while cl != 1:
            pass
        # # final_link_results=common_links
        # # final_link_results+=uncommon_links
        # # for i in final_link_results:
        # # print i
        # # print len(final_link_results)
        analysis(len(common_links), len(list(set(all_links))))
        final_link_results = final_link_results[:10]
        print "\n\n ** Top 10 Results ** \n\n"
        for element in final_link_results:
            print element
        if len(cache) <= 50:
            cache[query] = list(final_link_results)
        else:
            cache.pop(0)
            cache[query] = list(final_link_results)
        with open('cache.json', 'w') as jfile:
            json.dump(cache, jfile)


main()
