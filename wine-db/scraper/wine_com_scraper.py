#!/usr/bin/env python3

from subprocess import run, PIPE, STDOUT
import multiprocessing
import itertools
import json
from re import sub
from lxml import html
import requests

DATA_INFILE = './winecom_urls.txt'
DATA_OUTFILE = './winecom.json'
ERR_FILENAME = './errors.log'
BASE_URL = 'http://www.wine.com'
N = 50
PREV_RUN = run(
    ['wc', '-l', DATA_OUTFILE],
    stdout = PIPE,
    stderr = STDOUT
)
if PREV_RUN.returncode == 1:
    PREV_RUN = 0
else:
    PREV_RUN = PREV_RUN.stdout.decode()
    PREV_RUN = int(sub(r' +([0-9]+).*', r'\1', PREV_RUN))


def read_wine_urls(infile):
    with open(infile, 'r') as data:
        for row in data:
            yield row


def save_wine(wineData, outfile):
    with open(outfile, mode = 'a') as f:
        json.dump(wineData, f)
        f.write('\n')


def get_wine(wine):
    page = requests.get(BASE_URL + wine)
    if page.status_code != 200:
        with open(ERR_FILENAME, mode = 'a') as f:
            f.write(wine + '\n')
        return

    page = html.fromstring(page.content)
    wineData = {}
    
    # This is terrible and makes me want to cry
    # but I also don't care enough to make it
    # not suck. Dilemmas.
    try:
        wineData['Wine Name'] = page.xpath(
            '//h1[@class="pipName"]//text()')[0]
    except IndexError:
        wineData['Wine Name'] = ''

    try:
        wineData['Varietal'] = page.xpath(
            '//span[@class="prodItemInfo_varietal"]//text()')[0]
    except IndexError:
        wineData['Varietal'] = ''

    try:
        wineData['Origin'] = page.xpath(
            '//span[@class="prodItemInfo_originText"]//text()')[0]
    except IndexError:
        wineData['Origin'] = ''

    wineData['Ratings'] = page.xpath('//ul[@class="wineRatings_list"]//text()')

    try:
        wineData['Price'] = page.xpath(
            '//link[@class="productPrice_price-itemProp"]')[0].attrib['content']
    except IndexError:
        wineData['Price'] = ''

    try:
        wineData['Winemaker\'s Notes'] = page.xpath(
            '//div[@class="pipWineNotes"]//div//div//text()')[0]
    except IndexError:
        wineData['Winemaker\'s Notes'] = ''
    
    try:
        wineData['Critical Reviews'] = page.xpath(
            '//p[@class="pipProfessionalReviews_review"]//span//text()')
    except IndexError:
        wineData['Critical Reviews'] = ''
    
    save_wine(wineData, DATA_OUTFILE)


if __name__ == '__main__':
    pool = multiprocessing.Pool(None)
    wines = read_wine_urls(DATA_INFILE)
    for _ in range(PREV_RUN):
        next(wines)

    while True:
        results = pool.map(get_wine, itertools.islice(wines, N))
        if not results:
            break
