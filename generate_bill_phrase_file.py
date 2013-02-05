# -*- coding: utf-8 -*-

from optparse import OptionParser

import os

from nltk.corpus import stopwords
from nltk import wordpunct_tokenize, ingrams

stopwords_new = stopwords.words('english')
stopwords_new.append(["nbsp", "javascript", "pagetracker", "http", "https"])

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)

# python generate_bill_phrase_file.py --dir=bills --out=bill-phrases.txt

def _remove_stopwords_lowercase(words):
    """
    Remove stopwords, convert all words to lowercase, exclude numbers
    """
    return [w.lower() for w in words if not w.lower()
        in stopwords_new and w.isalpha()]

def ngram_phrases(t, n):
    tokens = wordpunct_tokenize(t)
    tokens = _remove_stopwords_lowercase(tokens)
    return set(' '.join(n_grams) for n_grams in ingrams(tokens, n))

def phrases(fi):
    text = open(fi,'r').read()
    return sorted(list(ngram_phrases(text, 8)))

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-d", "--dir", dest="data_dir", default=None, help="Data directory", metavar="FILE")
    parser.add_option("-o", "--out", dest="out", default=None, help="Outfile", metavar="FILE")
    (options, args) = parser.parse_args()

    logger.setLevel(logging.DEBUG)

    files = [ os.path.join(options.data_dir,f) for f in os.listdir(options.data_dir) if f.endswith('.txt') ]

    o = open(options.out,'w')
    for f in files:
        logger.info('Processing %s' % f)
        for phrase in phrases(f):
            p = f.split('/') # Get the filename from the full path
            o.write('%s\t%s\t%s\n' % (f,p[-1][:2],phrase)) # File, state, phrase
    o.close()