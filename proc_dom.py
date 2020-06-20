from re import sub
import sys

for line in sys.stdin:
    #print(line)
    print(sub("\s+", ",", line.strip()))
