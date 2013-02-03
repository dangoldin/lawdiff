# n-gram-splitter

""" Has a class called langmodel that takes a text and creates an NLTK FreqDist object
    that has counts of unigrams, bigrams, and trigrams.

    Example Usage:

    s = "This is a test string. This is a test string. This is a test string. This is a test string. This is a test string. This is a test string. This is a test string. This is a test string."
    test_lang_model = lang_model(s)

    To access word counts of a specific n-gram:
    - e.g. for unigrams
    test_lang_model.uni_fd.count(<<WORD>>)

    List of Strings
    test_lang_model.uni_fd.keys()

    List of Tuples with (STRING, COUNT)
    test_lang_model.uni_fd.items()
"""

from nltk.corpus import stopwords
from nltk import FreqDist, wordpunct_tokenize, cluster, ingrams

stopwords_new = stopwords.words('english')
stopwords_new.append(["nbsp", "javascript", "pagetracker", "http", "https"])


def _sliding_window(l, n):
    return [tuple(l[i:i + n]) for i in range(len(l) - n + 1)]


def _remove_stopwords_lowercase(words):
    """
    Remove stopwords, convert all words to lowercase, exclude numbers
    """
    return [w.lower() for w in words if not w.lower()
        in stopwords_new and w.isalpha()]


def make_ngram_tuples(l, n):
    l = _remove_stopwords_lowercase(l)
    t = _sliding_window(l, n)
    phrase_list = []
    if n == 1:
        phrase_list = [s for (s,) in t]
    else:
        list_of_tuples = [(tuple(s[:-1]), s[-1]) for s in t]
        for phrase in list_of_tuples:
            #print phrase
            if n == 2:
                phrase_list.append("%s %s" % (phrase[0][0], phrase[1]))
            if n == 3:
                phrase_list.append("%s %s %s" % (phrase[0][0], phrase[0][1], phrase[1]))
    return phrase_list

def ngrams(l, n):
    l = _remove_stopwords_lowercase(l)
    phrase_list = []
    for n_grams in ingrams(l, n):
        phrase_list.append(' '.join(n_grams))
    return phrase_list

class lang_model():
    """Creates a language model of given text"""
    def __init__(self, text):
        self.tokens = wordpunct_tokenize(text)
        # self.unigram = make_ngram_tuples(tokens, 1)
        # self.bigram = make_ngram_tuples(tokens, 2)
        # self.trigram = make_ngram_tuples(tokens, 3)
        # self.uni_fd = FreqDist(self.unigram)
        # self.bi_fd = FreqDist(self.bigram)
        # self.tri_fd = FreqDist(self.trigram)
        #self.big_gram = make_ngram_tuples(tokens, 8)
        self.big_gram = ngrams(self.tokens,8)
        self.big_fd = FreqDist(self.big_gram)

    def gram(self, size):
        return ngrams(self.tokens, size)

if __name__ == '__main__':
    s = "This is a test string. This is a test string. This is a test string. This is a test string. This is a test string. This is a test string. This is a test string. This is a test string."
    test_lang_model = lang_model(s)
    print test_lang_model.uni_fd.items()
