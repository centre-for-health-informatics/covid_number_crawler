from bs4 import BeautifulSoup
import urllib.request
import re
import requests
import numpy as np
import spacy
import time
import datetime
import json

nlp = spacy.load('en_core_web_sm')

def match_num(text):
    number_words = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety', 'hundred','hundreds', 'thousand','thousands']
    text = text.replace('COVID-19',' ')
    has_digit = re.search('\d+',text)
    if not has_digit:
        for word in number_words:
            pattern = ' ' + word + ' '
            if re.search(pattern,text):
                has_digit = True
                break
    return has_digit

def get_links():
    resp = urllib.request.urlopen("https://globalnews.ca/?s=alberta+coronavirus")
    soup = BeautifulSoup(resp, from_encoding=resp.info().get_param('charset'))
    link_list = []
    pattern = 'https://globalnews.ca/news/\d+/.*/$'
    for link in soup.find_all('a', href=True):
        if re.match(pattern,link['href']):
            link_list.append(link['href'])
        link_set = set(link_list)
    unique_link_list = list(link_set)
    return unique_link_list

def show_sents(unique_link_list):
    data = {}
    data['article'] = []
    for link in unique_link_list:
        time.sleep(1)
        article = requests.get(link)
        article_content = article.content
        soup_article = BeautifulSoup(article_content, 'html.parser')
        # Show date
        post_time =soup_article.find_all('div', class_='c-byline__date')
        date =[]
        for t in post_time:
            date.append(t.get_text())
        # Show number related phrase
        body = soup_article.find_all('div')#, class_='l-article__part'
        x = body[0].find_all('p')
        news_contents = ''
        # Unifying the paragraphs
        list_paragraphs = []
        for p in np.arange(0, len(x)):
            paragraph = x[p].get_text()
            if not 'read more' in  paragraph.lower():
                list_paragraphs.append(paragraph)
            final_article = " ".join(list_paragraphs)
        spacy_doc = nlp(final_article)
        related_text = ""
        for sent in spacy_doc.sents:
            if 'case' in sent.text and 'new' in sent.text:
                if match_num(sent.text):
                    clean_text = sent.text.replace('\n',' ')
                    clean_text = clean_text.replace('\t','')
                    related_text =related_text + clean_text + '\n'
        if related_text:
            data['article'].append({
                'title': soup_article.title.get_text(),
                'date': date,
                'text': related_text,
            })
        with open('data.txt', 'a') as outfile:
            json.dump(data, outfile)

prev_set = set()
while True:
    unique_link_list = get_links()
    new_link = list(set(unique_link_list).difference(prev_set))
    if new_link:
        print(datetime.datetime.now())
        text = show_sents(new_link)
    prev_set = set(unique_link_list)
    time.sleep(3600)