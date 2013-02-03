from optparse import OptionParser
import difflib
import re

from compare_bills import get_comparison_set

# python generate_diff.py --file1=test/file1.txt --file2=test/file2.txt

RE_SPLIT = re.compile(r'([\s+\W+])', flags=re.IGNORECASE)

def generate_diff(fi1,fi2):
    # Modified code from https://github.com/aaronsw/htmldiff

    a = RE_SPLIT.split(open(fi1).read())
    b = RE_SPLIT.split(open(fi2).read())

    out = []
    s = difflib.SequenceMatcher(None, a, b, autojunk=False)
    for e in s.get_opcodes():
        if e[0] == "replace":
            out.append('<del class="modified">'+''.join(a[e[1]:e[2]]) + '</del><ins class="modified">'+''.join(b[e[3]:e[4]])+"</ins>")
        elif e[0] == "delete":
            out.append('<del>'+ ''.join(a[e[1]:e[2]]) + "</del>")
        elif e[0] == "insert":
            out.append('<ins>'+''.join(b[e[3]:e[4]]) + "</ins>")
        elif e[0] == "equal":
            out.append(''.join(b[e[3]:e[4]]))
        else:
            raise "Um, something's broken. I didn't expect a '" + `e[0]` + "'."
    return ''.join(out)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-f", "--file1", dest="file1", default=None, help="First file", metavar="FILE")
    parser.add_option("-g", "--file2", dest="file2", default=None, help="Second file", metavar="FILE")
    (options, args) = parser.parse_args()
    f1 = options.file1
    f2 = options.file2

    t = generate_diff(f1,f2)
    f = open('out.html','w')
    f.write("""
        <html>
        <head>
            <title>File diff %s vs %s</title>
            <style>
                del { background:#ffe6e6; }
                ins { background:#e6ffe6; }
                del.mod { background:#fff3e6; }
                ins.mod { background:#fff3e6; }
            </style>
        </head>
        <body>
            %s
        </body>
        </html>
    """ % (f1,f2,t))
    f.close()