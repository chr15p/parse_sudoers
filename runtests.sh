#!/bin/bash

TMPFILE=$(mktemp)

WORKDIR=$(pwd)
TESTDIR=$WORKDIR/tests
TESTS=${@:-$(ls ${TESTDIR}/*-sudoers)}

for FILE in $TESTS; do
    
    OUTFILE=${FILE}-yaml
    if [ -f ${OUTFILE} ]; then
        ${WORKDIR}/parse_sudoers.py -f ${FILE} -a > $TMPFILE

        DIFFS=$(diff -q $TMPFILE $OUTFILE)
        DIFFS=$(${WORKDIR}/difftasklists.py $TMPFILE $OUTFILE)
        if [ $? -eq 0 ]; then
            echo "PASSED $FILE"
        else
            echo "$TMPFILE $OUTFILE"
            echo "FAILED $FILE"
            echo "$DIFFS"
            exit
        fi

    fi

done

