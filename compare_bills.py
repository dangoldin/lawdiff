import os
from itertools import combinations

import difflib

from n_gram_splitter import lang_model

import Queue
import threading

data_dir = 'bills/all'

MIN_LINES = 100
MIN_TRIGRAMS = 3
MIN_BIGRAMS = 3

comparison_results = []

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
    t = f.read().replace('\n',' ').replace('\r',' ')
    l = lang_model(t)
    p = set()
    for phrase, cnt in l.big_fd.iteritems():
        p.add(phrase)
        # if cnt >= MIN_BIGRAMS:
        #     p.add(phrase)
        # else:
        #     break
    return p

def print_set_difference(s1, s2):
    phrases = sorted(list(s1.union(s2)))
    phrases = sorted(phrases, key=lambda x:1 if x in s1 and x in s2 else 0, reverse=True)
    for phrase in phrases:
        in_1 = 'X' if phrase in s1 else ' '
        in_2 = 'X' if phrase in s2 else ' '
        if phrase in s1 and phrase in s2:
            print '%s %s : %s' % (in_1, in_2, phrase)

def compare(file1, file2):
    #s = difflib.SequenceMatcher(None, t1, t2)
    #score = s.ratio()

    p1 = get_comparison_set(file1)
    p2 = get_comparison_set(file2)

    score = float(len(p1.intersection(p2)))/len(p1.union(p2))
    #score = float(len(p1.intersection(p2)))

    if score > 0:
        print '%s vs %s' % (file1, file2)
        print_set_difference(p1,p2)
        comparison_results.append((file1,file2,score))

    print '%s,%s: %f' % (file1,file2,round(score, 3))

    return (file1, file2, score)

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

class Comparer(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            f1, f2 = self.queue.get()
            self.compare_bills(f1, f2)
            self.queue.task_done()

            if self.queue.empty():
                print 'Final results:',comparison_results

    def compare_bills(self, file1, file2):
        compare(file1,file2)

if __name__ == '__main__':
    # compare('bills/ARB00002682.txt','bills/ARB00002682.txt')
    # exit()

    # compare('test/test-bill1.txt','test/test-bill2.txt')
    # exit()

    # compare('bills/ARB00002682.txt', 'bills/FLB00002163.txt')
    # exit()

    files = [os.path.join(data_dir,f) for f in os.listdir(data_dir) if f.endswith('.txt')]

    keep_files = [f for f in files if keep_file(f)]
    print 'Kept files:', keep_files

    pairs = combinations(keep_files, 2)

    queue = Queue.Queue()

    for i in range(8):
        t = Comparer(queue)
        t.setDaemon(True)
        t.start()

    for pair in pairs:
        if keep_pair(*pair):
            queue.put(pair)

    queue.join()

    # comparisons = [compare(*pair) for pair in pairs if keep_pair(*pair)]

    # comparisons_s = sorted(comparisons, key=lambda x: x[2], reverse=True)

    # print comparisons_s