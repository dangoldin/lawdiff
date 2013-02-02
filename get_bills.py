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

import html2text

data_dir = 'bills'

def to_unicode_or_bust(obj, encoding='utf-8'):
    if isinstance(obj, basestring):
        if not isinstance(obj, unicode):
            obj = unicode(obj, encoding)
    return obj

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
    s = s.decode("windows-1252")
    #s = unicode(s)
    s = s.encode('utf8', 'ignore')
    #print 'First',s
    #s = unidecode(unicode(s))
    #print 'Second',s
    # h = html2text.HTML2Text()
    # h.ignore_links = True
    # s = h.handle(s)
    #print 'Final',s
    return s

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
        if doc_url.lower().endswith('.pdf'):
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
    agro_bills = sunlight.openstates.bills(
        q='agriculture',
        chamber='upper'
    )

    print 'Retrieved %d bills' % len(agro_bills)

    for bill in agro_bills:
        if bill['type'][0] == 'bill':
            bill_id = bill['id']
            #print bill['state'], bill['title'], bill['bill_id']
            #print bill['bill_id']
            if file_exists(os.path.join(data_dir,'%s.txt' % bill_id)):
                print 'Bill %s already downloaded' % bill_id
            else:
                print 'Getting bill %s' % bill_id
                get_bill(bill_id)