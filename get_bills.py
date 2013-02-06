# -*- coding: utf-8 -*-

from optparse import OptionParser

import Queue
import threading

import os
import re
import urllib, urllib2
from unidecode import unidecode

import sunlight

from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from cStringIO import StringIO

import state_data

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)

RE_BODY = re.compile(r'<body.+?>.+</body>', re.DOTALL)
RE_SCRIPT = re.compile(r'<script.+?>.+?</script>', re.DOTALL)
RE_HTML = re.compile(r'<.+?>', re.DOTALL)

# python get_bills.py --dir=bills --state=ar -v

def get_content_type(url):
    page = urllib2.urlopen(url)
    return page.headers.getheader('content-type')

def file_exists(path):
    try:
        with open(path) as f:
            return True
    except IOError as e:
        return False

def convert_html(path):
    fp = file(path, 'r')
    s = fp.read()
    c = RE_BODY.search(s).group(0)
    c = RE_SCRIPT.sub('',c)
    c = RE_HTML.sub('',c)
    return c

def convert_pdf(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)

    fp = file(path, 'rb')
    process_pdf(rsrcmgr, device, fp)
    fp.close()
    device.close()

    s = retstr.getvalue()
    retstr.close()
    return s

def get_bill_document_url(bill_id):
    bill = sunlight.openstates.bill(
        bill_id=bill_id,
    )
    documents = bill['documents']
    if len(documents) > 0:
        return documents[0]['url']
    else:
        logger.error('Bill %s has no documents' % bill_id)
        return ''

def download_bill(doc_url, data_dir, bill_id):
    content_type = get_content_type(doc_url)
    logger.debug('Content Type: %s' % content_type)
    file_path = None
    if 'pdf' in content_type or doc_url.lower().endswith('.pdf'):
        file_path = os.path.join(data_dir, '%s.pdf' % bill_id)
        urllib.urlretrieve(doc_url, file_path)
    elif 'html' in content_type or doc_url.lower().endswith('.html') or doc_url.lower().endswith('.htm'):
        file_path = os.path.join(data_dir, '%s.html' % bill_id)
        urllib.urlretrieve(doc_url, file_path)
    else:
        logger.error('Can\'t determine extension for bill %s' % doc_url)
    return file_path

def convert_bill_to_text(file_path, data_dir, bill_id):
    s = None
    if file_path.endswith('.pdf'):
        s = convert_pdf(file_path)
        new_file_path = file_path.replace('.pdf', '.txt')
    elif file_path.endswith('.html'):
        s = convert_html(file_path)
        new_file_path = file_path.replace('.html', '.txt')
    else:
        logger.error('Could not process file %s' % file_path)
    if s and s.strip():
        f = open(new_file_path,'w')
        f.write(s)
        f.close()

class Downloader(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            bill_id, data_dir = self.queue.get()
            self.get_bill(bill_id, data_dir)
            self.queue.task_done()

    def get_bill(self, bill_id, data_dir):
        # Check if bill has already been downloaded
        if file_exists(os.path.join(data_dir,'%s.txt' % bill_id)):
            logger.info('Bill %s has already been downloaded' % bill_id)
        else:
            doc_url = file_path = None
            logger.info('Getting bill %s' % bill_id)
            doc_url = get_bill_document_url(bill_id)
            if doc_url:
                file_path = download_bill(doc_url, data_dir, bill_id)
            if file_path:
                convert_bill_to_text(file_path, data_dir, bill_id)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-d", "--dir", dest="data_dir", default=None, help="Data directory", metavar="FILE")
    parser.add_option("-s", "--state", dest="state", default=None, help="State codes")
    parser.add_option("-q", "--query", dest="query", default=None, help="Search query")
    parser.add_option("-w", "--search_window", dest="search_window", default="session", help="Search window")
    parser.add_option("-t", "--type", dest="type", default="bill", help="Search type")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=None, help="Turns on verbose loggin")
    (options, args) = parser.parse_args()
    state_codes = state_data.state_abbr if options.state == 'all' else options.state.split(',')

    if options.verbose: logger.setLevel(logging.DEBUG)

    bills = []
    for state in state_codes:
        logger.info('Retrieving bill ids for %s' % state)
        kwargs = {'state' : state.lower(),
                'search_window' : options.search_window,
                'type' : options.type,
                }
        if options.query:
            kwargs['q'] = options.query
        state_bills = sunlight.openstates.bills(**kwargs)
        logger.info('Retrieved %d bill ids for state %s' % (len(state_bills), state))
        bills.extend(state_bills)

    logger.info('Retrieved %d total bill ids' % len(bills))

    queue = Queue.Queue()

    for i in range(8):
        t = Downloader(queue)
        t.setDaemon(True)
        t.start()

    for bill in bills:
        queue.put((bill['id'], options.data_dir))

    queue.join()