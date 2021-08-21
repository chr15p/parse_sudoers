#!/bin/bash


TMPDIR=$(mktemp -d)


TESTDIR=./tests
TESTS=${@:-$(ls ${TESTDIR}/*-sudoers)}

WORKDIR=$TMPDIR/$TESTDIR
mkdir $WORKDIR

for FILE in $TESTS; do
    
    OUTFILE=${FILE}.yaml
    ./parse_sudoers.py -f ${FILE} -a > $TMPDIR/$OUTFILE

done

ansible-playbook -vv -i inventory --extra-vars TESTLOCATION=$WORKDIR tests_playbook.yaml

rm -rf $TMPDIR
