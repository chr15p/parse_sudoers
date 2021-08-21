#!/usr/bin/env python

import sys
import yaml
from deepdiff import DeepDiff

#def yaml_as_dict(my_file):
#    my_dict = {}
#    with open(my_file, 'r') as fp:
#        docs = yaml.safe_load_all(fp)
#        #for doc in docs:
#        #    for key, value in doc.items():
#        #        my_dict[key] = value
#    #return my_dict
#    print(docs)
#    return docs

def yaml_as_dict(my_file):
    with open(my_file, 'r') as stream:
        try:
            contents1 = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    #print(contents1)
    return contents1


if __name__ == '__main__':
    a = yaml_as_dict(sys.argv[1])
    b = yaml_as_dict(sys.argv[2])
    ddiff = DeepDiff(a, b, ignore_order=True)
    print(ddiff)

    exit(len(ddiff.keys()))
