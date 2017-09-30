from re import sub, findall
import requests
from lxml import html

DATA_FILENAME = './winemag.txt'
BASE_URL = 'http://www.winemag.com/?s=&drink_type=wine&sort_by=vintage&sort_dir=desc&page='
HEADERS = {'User-Agent': 'Mozilla/5.0'}       

def get_pages(url):
    page = requests.get(url + '0', headers = HEADERS)
    page = html.fromstring(page.content)
    results = page.xpath(
        '//div[@class=\'pagination\']//ul//li//a//text()'
    )[-1]

    return results

def save_wine(outfile, wineData):
    with open(outfile, mode = 'a') as f:
        f.write('{0}\n'.format(wineData))

maxPage = int(get_pages(BASE_URL))

for i in range(1, maxPage):
    page = requests.get(BASE_URL + str(i), headers = HEADERS)  
    page = html.fromstring(page.content)  
    wines = page.xpath('//a[@class=\'review-listing\']')
    wines = [elem.attrib['href'] for elem in wines]
    for link in wines:
        save_wine(DATA_FILENAME, str(link))