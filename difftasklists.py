#!/usr/bin/env python

import yaml
import sys

file1=sys.argv[1]
file2=sys.argv[2]

with open(file1, 'r') as stream:
    try:
        contents1 = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

with open(file2, 'r') as stream:
    try:
        contents2 = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

#print(contents1)
#print(contents2)
#exit(0)

count=0
for task in contents1:
    #print(task)
    if task not in contents2:
        print("no match: %s"%task)
        count+=1

exit(count)
