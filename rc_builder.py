#!/usr/bin/env python
"""
AskReddit based corpus builder
In development
"""
__author__ = "deniederhut"
__version__ = "0.0.1"

import requests, re, io, time, json
from lxml import etree


headers = {
    'User-Agent' : 'redicorpus v. 0.0.1',
    'From' : 'dillon.niederhut@gmail.com'
}
page = requests.get('http://reddit.com/r/Askreddit/.xml', headers = headers)
data = etree.XML(page.content)

links = list()
for element in data.iter('guid'):
    links.append(element.text)

for i in links:
    url = str(i+".json/?limit=500/?depth=100")
    page = requests.get(url,headers = headers).content
    name = print "pages/" + time.strftime("%Y_%m_%d") + re.search(r'[^http://www.reddit.com/r/AskReddit/comments/].{5,5}', i).group() + ".txt"
    with io.open(name, 'w', encoding = 'utf-8') as f:
        f.write(unicode(json.dumps(page, esure_ascii = False)))
    time.sleep(2)

