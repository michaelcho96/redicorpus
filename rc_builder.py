#!/usr/bin/env python
"""
AskReddit-based corpus builder
In development
"""
__author__ = "Dillon Niederhut"
__version__ = "0.0.1"
__email__ = "dillon.niederhut@gmail.com"

import requests, re, io, time, os
from lxml import etree
 
page = requests.get('http://reddit.com/r/Askreddit/.xml', headers = {
    'User-Agent' : 'redicorpus v. ' + __version__,
    'From' : __email__
}).content

links = list()
for element in page.iter('guid'):
    links.append(element.text)

try:
    os.makedirs(os.getcwd() + "/redicorpus/pages/" + time.strftime("%Y_%m_%d"))
except OSError:
    if not os.path.isdir(os.getcwd() + "/redicorpus/pages/" + time.strftime("%Y_%m_%d")):
        raise
os.chdir(os.getcwd() + "/redicorpus/pages/" + time.strftime("%Y_%m_%d"))

for i in links:
    url = str(i+".json/?limit=500/?depth=100")
    page = requests.get(url,headers = headers).content
    name = print re.search(r'[^http://www.reddit.com/r/AskReddit/comments/].{5,5}', i).group() + ".txt"
    with io.open(name, 'w', encoding = 'utf-8') as f:
        f.write(unicode(json.dumps(page, esure_ascii = False)))
    time.sleep(2)

page = requests.get('http://www.reddit.com/r/AskReddit/comments/2dzc2f/what_is_a_completely_rational_sentence_you_could/.json', headers = {
    'User-Agent' : 'redicorpus v. ' + __version__,
    'From' : __email__
})

f = open('Example.json', 'w')
f.write(page.content)
f.close()

