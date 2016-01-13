#!/opt/bin/python3

import sys
import mtfcoding2

if len(sys.argv) < 2:
    print("usage: ./mtfdecode.py <filename>")
    sys.exit(1)

mtfcoding2.decode(sys.argv[1])
