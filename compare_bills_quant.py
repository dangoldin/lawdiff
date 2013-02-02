import os
from itertools import combinations

import difflib

from n_gram_splitter import lang_model

data_dir = 'bills'

MIN_LINES = 200
MIN_TRIGRAMS = 3
MIN_BIGRAMS = 3

def memoize(f):
    """ Memoization decorator for functions taking one or more arguments. """
    class memodict(dict):
        def __init__(self, f):
            self.f = f
        def __call__(self, *args):
            return self[args]
        def __missing__(self, key):
            ret = self[key] = self.f(*key)
            return ret
    return memodict(f)

@memoize
def get_comparison_set(fi):
    f = open(fi,'r')
    text = f.read()
    lang = lang_model(text)
    return lang.trigram

def print_set_difference(s1, s2):
    phrases = sorted(list(s1.union(s2)))
    for phrase in phrases:
        in_1 = 'X' if phrase in s1 else ' '
        in_2 = 'X' if phrase in s2 else ' '
        print '%s %s : %s' % (in_1, in_2, phrase)

def compare(file1, file2):
    #s = difflib.SequenceMatcher(None, t1, t2)
    #score = s.ratio()

    p1 = get_comparison_set(file1)
    p2 = get_comparison_set(file2)

    common_phrases = []
    similarity = 0
    for quant in p1:
        if quant in p2:

            common_phrases.append(quant)
            similarity = similarity + 1
    print common_phrases
    return "Similarity: %s" % similarity

def keep_file(fi):
    f = open(fi, 'r')

    lines = f.readlines()
    if len(lines) < MIN_LINES:
        return False
    return True

def keep_pair(f1, f2):
    p1 = os.path.split(f1)
    p2 = os.path.split(f2)
    if p1[1][:2] == p2[1][:2]:
        return False
    return True

if __name__ == '__main__':
    # compare('bills/ARB00002682.txt','bills/ARB00002682.txt')
    # exit()

    # compare('test/test-bill1.txt','test/test-bill2.txt')
    # exit()

    compare('bills/ARB00002682.txt', 'bills/FLB00002163.txt')
    exit()

    files = [os.path.join(data_dir,f) for f in os.listdir('bills')]

    keep_files = [f for f in files if keep_file(f)]
    print 'Kept files:', keep_files

    pairs = combinations(keep_files, 2)
    comparisons = [compare(*pair) for pair in pairs if keep_pair(*pair)]

    comparisons_s = sorted(comparisons, key=lambda x: x[2], reverse=True)

    print comparisons_s
