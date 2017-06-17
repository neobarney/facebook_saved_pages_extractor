
# coding: utf-8

# In[ ]:

import requests
from lxml import etree
import json
import urllib
from pandas import DataFrame 
import pandas as pd


cookie = '' #paste your fb connection cookie here 
collection_token = '' #paste your fb collection token here 

headers = {
    'cookie': cookie,
}

params = (
    ['cursor', ''],
    ('collection_token', collection_token),
    ('__a', '1'),
)




def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def update_cursor(params, cursor):
    params[0][1] = cursor
    return params

    
response_texts = []
results = []
params_list = []
cursor = ''
cnt = 0
response = requests.get('https://www.facebook.com/saved/more/', headers=headers, params=params)
   
while True: 
    print results[-12:]
    cnt+=1
    response_texts.append(response.text)
    x= response.text.replace('\\\\',"""\\""")

    parsed = json.loads(response.text[9:])
    html = parsed['domops'][0][3]['__html']
    raw_cursor = find_between(response.text,
             'cursor=', '&')
    pos_escape_character = raw_cursor.find('\\u')
    cursor = raw_cursor[:pos_escape_character] + raw_cursor[pos_escape_character:1000].decode('unicode-escape')
    cursor = urllib.unquote(cursor)
    html_ok = html.replace('\\','')
    tree = etree.HTML(html_ok)
    href_xpath = """/html/body/div/div/div/div/div/div/a/@href"""
    title_xpath = """/html/body/div/div/div/div/div/div/a/span/text()"""
    urls_lst = tree.xpath(href_xpath)
    urls = [u for u in urls_lst if u<>'#']
    titles_lst = tree.xpath(title_xpath)
    titles = [u for u in titles_lst]
    
    results = results + zip(titles, urls)
    print len(results)
    if cursor=='':
        break
    else:
        new_params = update_cursor(params, cursor)
        response = requests.get('https://www.facebook.com/saved/more/', headers=headers, 
                                 params=new_params)
        
        params_list.append(new_params)


df = DataFrame(results,columns=['title','link'])
excel_filename = '/root/data3/facebook_links.xlsx'

writer = pd.ExcelWriter(excel_filename)
df.to_excel(writer,'Sheet1')
writer.save()
print('Successfully exported {0} links to {1}'.format(len(results), excel_filename))

