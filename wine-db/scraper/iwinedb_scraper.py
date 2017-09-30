#!/usr/bin/env python3

from subprocess import run, PIPE, STDOUT
import multiprocessing
import json
from re import sub
from lxml import html
import requests

DATA_FILENAME = './iwinedb.json'
ERR_FILENAME = './errors.log'
PREV_RUN = run(
    ['wc', '-l', './iwinedb.json'],
    stdout = PIPE,
    stderr = STDOUT
)

if PREV_RUN.returncode == 1:
    PREV_RUN = 0
else:
    PREV_RUN = PREV_RUN.stdout.decode()
    PREV_RUN = int(sub(r' +([0-9]+).*', r'\1', PREV_RUN))

START_POS = 147045 + int(PREV_RUN)
END_POS = 309806
BASE_URL = 'http://www.iwinedb.com/WineDetails.aspx?wid='


def save_wine(outfile, wineData):
    with open(outfile, mode = 'a') as f:
        json.dump(wineData, f)
        f.write('\n')


def download_wine(wineId):
    page = requests.get(BASE_URL + str(wineId))

    if page.status_code != 200:
        with open(ERR_FILENAME, mode = 'a') as f:
            f.write(str(wineId) + '\n')
        return

    tree = html.fromstring(page.content)

    wineName = tree.xpath('//span[@id="LabelWineTitle"]//text()')
    wineName = str(wineName[0])

    detailedInformation = tree.xpath('//table[@id="Table5"]//tr//td//text()')
    detailedInformation[:] = [
        sub(
            r'([\r]+|[\n]+|[\t]+|  +)',
            '',
            elem
        ) for elem in detailedInformation
    ]

    indices = [
        idx for idx,
        elem in enumerate(detailedInformation)
        if ':' in elem
        or 'Winemaker\'s Notes' in elem
    ]

    indices = [
        idx for idx, elem in enumerate(detailedInformation)
        if ':' in elem
    ]

    wineDict = {}

    for elem in indices:
        wineDict[
            sub(r':', '', detailedInformation[elem])
        ] = detailedInformation[elem + 1]

    wineDict['Wine Name'] = wineName
    wineDict['Wine ID'] = wineId

    save_wine(DATA_FILENAME, wineDict)
    return


if __name__ == '__main__':
    pool = multiprocessing.Pool(None)
    wines = range(START_POS, END_POS)
    for i in pool.imap(download_wine, wines):
        pass
