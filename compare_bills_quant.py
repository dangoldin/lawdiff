import os
from itertools import combinations

from n_gram_splitter import lang_model
from optparse import OptionParser

data_dir = 'bills'

MIN_LINES = 100
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
def get_comparison_set(fi, ngram_length=8):
    f = open(fi,'r')
    text = f.read()
    lang = lang_model(text)
    return lang.gram(ngram_length)

def print_set_difference(s1, s2):
    phrases = sorted(list(s1.union(s2)))
    for phrase in phrases:
        in_1 = 'X' if phrase in s1 else ' '
        in_2 = 'X' if phrase in s2 else ' '
        print '%s %s : %s' % (in_1, in_2, phrase)


def compare_average(file1, file2):
   ngram_8 = compare(file1, file2, 8)
   ngram_10 = compare(file1, file2, 10)
   ngram_12 = compare(file1, file2, 12)

   return ngram_12[1] + ngram_10[1]/(ngram_12[1]*3) + ngram_8[1]/(ngram_10[1] * 3 * ngram_8[1] *6)


def compare(file1, file2, ngram_length=8):
    #s = difflib.SequenceMatcher(None, t1, t2)
    #score = s.ratio()

    p1 = get_comparison_set(file1, ngram_length)
    p2 = get_comparison_set(file2, ngram_length)

    common_phrases = []
    similarity = 0
    for quant in p1:
        if quant in p2:

            common_phrases.append(quant)
            similarity = similarity + 1
    return (common_phrases, similarity)

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
    
    parser = OptionParser()
    parser.add_option("-f", "--full-list", action="store_true", dest="full_list", default=None, help="Whether to loop through the whole list.  Defaults to test files")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=None, help="Turns on verbose loggin")
    (options, args) = parser.parse_args()
    if options.full_list:
       use_dir = data_dir
    else:
        use_dir = "test"

    files = [os.path.join(use_dir,f) for f in os.listdir(use_dir)]
        
    # Filter out short bills that arent really significant
    keep_files = [f for f in files if keep_file(f)]
    if options.verbose: print 'Kept files:', keep_files
    
    i = 0
    for f1 in keep_files:
        for f2 in keep_files[i:]:
            if f1 != f2:
                result = compare(f1, f2)
                if options.verbose: print result[0]

                print "%s, %s: %s" % (f1, f2, result[1]) 
                print compare_average(f1, f2)
        i = i + 1
#    pairs = combinations(keep_files, 2)
#    comparisons = [compare(*pair) for pair in pairs if keep_pair(*pair)]

#    comparisons_s = sorted(comparisons, key=lambda x: x[2], reverse=True)

#    print comparisons_s
