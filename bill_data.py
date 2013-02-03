import os

from compare_bills import get_comparison_set

data_dir = 'bills/all'

def summarize(fi):
    t = sorted(list(get_comparison_set(fi)))
    return t

if __name__ == '__main__':
    files = [os.path.join(data_dir,f) for f in os.listdir(data_dir) if f.endswith('.txt')]

    o = open('bill-data-dump.txt','w')
    for f in files:
        print 'Processing %s' % f
        for t in summarize(f):
            p = f.split('/')
            o.write('%s\t%s\t%s\n' % (f,p[-1][:2],t))
    o.close()