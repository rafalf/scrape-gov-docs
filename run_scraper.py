#!/usr/bin/env python


# win: pip install lxml==3.6.0  (other pip install lxml)
# pip install requests
# pip install
# pip install beautifulsoup4

import requests
from bs4 import BeautifulSoup
import os
import sys
import getopt
import logging
import time
import csv
import re

root_domain = 'https://www.sec.gov'
logger = logging.getLogger(os.path.basename(__file__))
latest = 'https://www.sec.gov/divisions/enforce/friactions.shtml'


def scrape(fld, fls):

    update = None

    # pull down archived files
    if fls == 'gov-urls':

        # read urls to scrape
        urls = []
        with open('gov_urls.txt', 'r') as h:
            for l in h:
                urls.append(l.strip())

    elif fls == 'update':

        urls = [latest]
        update = True
        down_ = _read_csv()
        docs_down = [d[0] for d in down_]

    # debug (testing purposes )
    # urls = ['https://www.sec.gov/divisions/enforce/friactions/friactions2005.shtml',
    #         'https://www.sec.gov/divisions/enforce/friactions/friactions2015.shtml']
    # urls = ['https://www.sec.gov/divisions/enforce/friactions/friactions2016.shtml']

    # scrape urls
    for url in urls:

        logger.info('Scraping: {}'.format(url))

        r = requests.get(url)

        if not fld:
            downloads_folder = os.path.join(os.path.dirname(__file__), 'download')
        else:
            downloads_folder = os.path.join(os.path.dirname(__file__), fld)
        if not os.path.isdir(downloads_folder):
            os.mkdir(downloads_folder)

        soup = BeautifulSoup(r.text, 'lxml')
        if url.count('2016') or url == latest:
            table = soup.find('table')
        else:
            table = soup.find_all('table')[-2]
        logger.debug('Rows in the table (incl. heading): {}'.format(len(table.find_all('tr'))))

        scraped_docs = []
        for row in table.find_all('tr'):
            cols = row.find_all('td')
            links = row.find_all('a')

            if len(links) == 0 or len(cols) == 1:
                logger.debug('Row ignored: {}'.format(cols))
                continue

            release_no = cols[0].text.strip()

            if update:
                if release_no in docs_down:
                    logger.info('Document already downloaded: {}'.format(release_no))
                    continue
                else:
                    logger.info('Document not yet download: {}'.format(release_no))

            # process date
            release_date = cols[1].text.strip()
            month = release_date[:3]
            day = release_date[release_date.find(' ') + 1:release_date.find(',')]
            year = release_date[-4:]
            # Ignore broken rows
            if not month or not day or not year:
                logger.debug('Row ignored: {}'.format(cols))
                continue

            release_date = '{}{}{}'.format(month, day, year)
            str_time = time.strptime(release_date, '%b%d%Y')
            f3_ = time.strftime('%d', str_time)
            f1_ = time.strftime('%Y', str_time)
            f2_ = time.strftime('%m', str_time)

            doc = [release_no, f1_, f2_, f3_]

            for link in links:
                href = link.get('href')
                logger.debug('Scrape href: {}'.format(href))
                doc.append(href)
                scraped_docs.append(doc)
                # process only first link
                break

        logger.debug('Scraped total docs: {}'.format(len(scraped_docs)))

        for doc_ in scraped_docs:

            movie_folder_y = os.path.join(downloads_folder, doc_[1])
            if not os.path.isdir(movie_folder_y):
                os.mkdir(movie_folder_y)

            movie_folder_m = os.path.join(movie_folder_y, doc_[2])
            if not os.path.isdir(movie_folder_m):
                os.mkdir(movie_folder_m)

            movie_folder = os.path.join(movie_folder_m, doc_[3])
            if not os.path.isdir(movie_folder):
                os.mkdir(movie_folder)

            get_url = '{}{}'.format(root_domain, doc_[4])
            logger.info('Download url: {}'.format(get_url))

            # html
            pdf = None
            if get_url.count('.htm'):
                dwn_as = os.path.join(movie_folder, doc_[0] + '.htm')
            elif get_url.count('.pdf'):
                dwn_as = os.path.join(movie_folder, get_url[get_url.rfind('/') + 1:])
                pdf = True
            logger.info('Download as: {}'.format(dwn_as))

            try:
                request = requests.get(get_url, timeout=30, stream=True)
                with open(dwn_as, 'wb') as fh:
                    for chunk in request.iter_content(1024 * 1024):
                        fh.write(chunk)
            except:
                logger.error('Something went wrong', exc_info=True)

            _write_row_csv(doc_)

            # .txt (process htm files)
            if not pdf:
                r_doc = requests.get(get_url)
                soup = BeautifulSoup(r_doc.text, 'lxml')
                texts = soup.findAll(text=True)

                dwn_as_txt = dwn_as[:-3] + 'txt'
                with open(dwn_as_txt, 'w') as f:
                    visible_elements = [_visible(elem) for elem in texts]
                    visible_text = ''.join(visible_elements)
                    f.write(visible_text)


def _visible(element):

    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return ""
    elif element.encode('utf-8') == '\n':
        return ""
    elif element.encode('utf-8').count('img src'):
        return ""
    elif re.match('<!--.*-->', element.encode('utf-8')):
        return ""
    return element.encode('utf-8') + "\n\n"


def _write_row_csv(row):
    with open('download.csv', 'ab') as hlr:
        wrt = csv.writer(hlr, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        wrt.writerow(row)
        logger.info('Row added to .csv file: {}'.format(row))


def _read_csv():
    with open('download.csv', 'rb') as hlr:
        rd = csv.reader(hlr, delimiter=',', quotechar='"')
        return [row for row in rd]


if __name__ == '__main__':
    dwn_folder = None
    verbose = None

    log_file = os.path.join(os.path.dirname(__file__), 'logs',
                                time.strftime('%d%m%y%H%M', time.localtime()) + "_scraper.log")
    file_hndlr = logging.FileHandler(log_file)
    logger.addHandler(file_hndlr)
    console = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(console)
    ch = logging.Formatter('[%(levelname)s] %(message)s')
    console.setFormatter(ch)
    file_hndlr.setFormatter(ch)

    argv = sys.argv[1:]
    opts, args = getopt.getopt(argv, "d:vf:", ["download=", "verbose", "files="])
    for opt, arg in opts:
        if opt in ("-f", "--folder"):
            dwn_folder = arg
        elif opt in ("-v", "--verbose"):
            verbose = True
        elif opt in ("-f", "--files"):
            files = arg

    if verbose:
        logger.setLevel(logging.getLevelName('DEBUG'))
    else:
        logger.setLevel(logging.getLevelName('INFO'))
    logger.debug('CLI args: {}'.format(opts))
    scrape(dwn_folder, files)
