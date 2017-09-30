#!/usr/bin/env python3

from subprocess import run, PIPE, STDOUT
import multiprocessing
import math
from re import sub
from lxml import html
import requests

DATA_FILENAME = './winecom_urls.txt'
BASE_URL = (
    'http://www.wine.com/v6/search/advancedsearchresults.aspx?' +
    'N=490&Ns=p_Vineyard|0&pagelength=100&Nao='
)


def round_up(x):
    return int(math.ceil(x / 100.0)) * 100


def get_pages(url):
    page = requests.get(url + '0')
    page = html.fromstring(page.content)
    results = page.xpath(
        '//span[@id=\'ctl00_BodyContent_ctrProducts_resultCountValue\']//text()'
    )[0]

    return int(results)


def save_wine(outfile, wineData):
    with open(outfile, mode = 'a') as f:
        for wine in wineData:
            f.write('{0}\n'.format(wine))


def download_wine_urls(wineId):
    page = requests.get(BASE_URL + str(wineId))
    page = html.fromstring(page.content)

    wines = page.xpath('//a[@class=\'listProductName\']')
    wines = [elem.attrib['href'] for elem in wines]

    save_wine(DATA_FILENAME, wines)
    return


if __name__ == '__main__':
    pool = multiprocessing.Pool(None)
    maxPage = round_up(get_pages(BASE_URL))
    wines = range(0, maxPage, 100)
    for i in pool.imap(download_wine_urls, wines):
        pass
