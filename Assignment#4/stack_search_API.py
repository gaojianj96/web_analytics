import json
import requests
import datetime
import HTMLParser

def stack_search(questionText):
    query_split=questionText.split('[')
    query_text=query_split[0]
    query_tag=''#"python%3Bjavascript"
    # for index in range(2,len(query_split)):
    for index in range(1, len(query_split)):
        tag=query_split[index].strip()
        if tag.strip() != '':
            if query_tag != '' and not query_tag.endswith('%3B'):
                query_tag += '%3B'
            query_tag += tag[:len(tag)-1]
    url="https://api.stackexchange.com/2.2/search/advanced?order=asc&sort=relevance&accepted=True&q={}&tagged={}&site=stackoverflow".format(query_text,query_tag)
    print url
    json_result=json.loads(requests.get(url).content)
    final_reults=[]
    json_result=HTMLParser.HTMLParser().unescape(json_result["items"])
    for item in json_result:
        if len(final_reults) >= 5:
            break
        url = item["link"]
        title=item["title"]
        count=item["answer_count"]
        time=datetime.datetime.fromtimestamp(item["creation_date"]).strftime('%b %d, %Y')
        final_reults.append([title, url, count, time])
    return final_reults