# -*- coding: utf-8 -*-

import urllib
import urllib2
import re
import os
from unidecode import unidecode

import sunlight

from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from cStringIO import StringIO

from state_codes import states

data_dir = 'bills'

RE_BODY = re.compile(r'<body.+?>.+</body>', re.DOTALL)
RE_HTML = re.compile(r'<.+?>', re.DOTALL)

def get_content_type(url):
    page = urllib2.urlopen(url)
    pageHeaders = page.headers
    contentType = pageHeaders.getheader('content-type')
    return contentType

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

def get_bill(bill_id):
    bill = sunlight.openstates.bill(
        bill_id=bill_id,
    )

    documents = bill['documents']
    if len(documents) > 0:
        try:
            doc_url = documents[0]['url']
        except Exception, e:
            print 'Could not get info for bill %s' % str(bill)
            return
    else:
        print 'Bill %s has no documents' % bill_id
        return

    s = None
    try:
        content_type = get_content_type(doc_url)
        print 'Content Type: %s' % content_type
        print 'URL: %s' % doc_url
        if content_type == 'application/pdf' or doc_url.lower().endswith('.pdf'):
            urllib.urlretrieve(doc_url, 'temp.pdf')
            s = convert_pdf('temp.pdf')
        elif content_type == 'text/html' or doc_url.lower().endswith('.html') or doc_url.lower().endswith('.htm'):
            urllib.urlretrieve(doc_url, 'temp.html')
            s = convert_html('temp.html')
        else:
            print 'Error - what do we do with file %s' % doc_url
            return
    except Exception, e:
        print 'Could not get %s: %s' % (doc_url, str(e))
        return

    f = open( os.path.join(data_dir, '%s.txt' % bill_id),'w')
    f.write(s)
    f.close()

if __name__ == '__main__':
    bills = sunlight.openstates.bills(
        q='gun',
    )

    print 'Retrieved %d bills' % len(bills)

    for bill in bills:
        if bill['type'][0] == 'bill':
            bill_id = bill['id']
            #print bill['state'], bill['title'], bill['bill_id']
            #print bill['bill_id']
            if file_exists(os.path.join(data_dir,'%s.txt' % bill_id)):
                print 'Bill %s already downloaded' % bill_id
            else:
                print 'Getting bill %s' % bill_id
                get_bill(bill_id)

    # bills = sunlight.openstates.bills(
    #         #subject = 'Guns',
    #         q='gun',
    #         state = 'ct',
    #         search_window = 'session',
    #         type = 'bill',
    #         chamber = 'upper',
    #     )

    # print bills

    # exit()
    # for state in states:
    #     bills = sunlight.openstates.bills(
    #         subjects = 'Guns',
    #         state = state.lower(),
    #         search_window = 'session',
    #         type = 'bill',
    #     )

    #     print state, len(bills)

    # exit()

    # for bill in bills:
    #     print bill['title']

    # exit()