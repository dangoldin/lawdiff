# -*- coding: utf-8 -*-

from optparse import OptionParser

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)

# python analyze_bill_phrase_file.py --in=bill-phrases.txt --out=bill-summary.txt

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-i", "--in", dest="infile", default=None, help="Infile", metavar="FILE")
    parser.add_option("-o", "--out", dest="out", default=None, help="Outfile", metavar="FILE")
    (options, args) = parser.parse_args()

    logger.setLevel(logging.DEBUG)

    logger.info('Step 1: Reading %s' % options.infile)
    phrases = {}
    f = open(options.infile,'r')
    for line in f:
        file_name, state, phrase = line.strip().split('\t')
        if phrase not in phrases:
            phrases[phrase] = { 'states' : set([state]), 'files': set([file_name]) }
        else:
            phrases[phrase]['states'].add(state)
            phrases[phrase]['files'].add(file_name)
    f.close()

    logger.info('Step 2: Writing %s' % options.out)
    f = open(options.out, 'w')
    g = open('all-' + options.out, 'w')
    for phrase, info in phrases.iteritems():
        if len(info['states']) > 1 and len(info['files']) > 1:
            f.write('%s\t%d\t%d\n' % (phrase, len(info['states']), len(info['files'])))
            for file_name in info['files']:
                g.write('%s\t%s\n' % (file_name, phrase))
    f.close()
    g.close()