#!/opt/bin/python3

import sys
import mtfcoding2

if len(sys.argv) < 2:
    print("usage: ./mtfencode.py <filename>")
    sys.exit(1)

mtfcoding2.encode(sys.argv[1])
