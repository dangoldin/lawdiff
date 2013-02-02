import os
from itertools import combinations

import difflib

data_dir = 'bills'

MIN_LINES = 200

def compare(file1, file2):
    f1 = open( file1, 'r')
    f2 = open( file2, 'r')

    t1 = f1.read()
    t2 = f2.read()

    s = difflib.SequenceMatcher(None, t1, t2)

    print '%s,%s: %f' % (file1,file2,round(s.ratio(), 3))

    return (file1, file2, s.ratio())

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
    files = [os.path.join(data_dir,f) for f in os.listdir('bills')]

    keep_files = [f for f in files if keep_file(f)]
    print 'Kept files:', keep_files

    pairs = combinations(keep_files, 2)
    comparisons = [compare(*pair) for pair in pairs if keep_pair(*pair)]

    comparisons_s = sorted(comparisons, key=lambda x: x[2], reverse=True)

    print comparisons_s