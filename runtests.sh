#!/bin/bash

TMPFILE=$(mktemp)

WORKDIR=$(pwd)
TESTDIR=$WORKDIR/tests
TESTS=${@:-$(ls ${TESTDIR}/*-sudoers)}

for FILE in $TESTS; do
    
    OUTFILE=${FILE}-yaml
    if [ -f ${OUTFILE} ]; then
        ${WORKDIR}/parse_sudoers.py -f ${FILE} -a > $TMPFILE

        #DIFFS=$(diff -q $TMPFILE $OUTFILE)
        DIFFS=$(${WORKDIR}/difftasklists.py $TMPFILE $OUTFILE)

        if [ -z "$DIFFS" ]; then
            echo "PASSED $FILE"
        else
            echo "FAILED $FILE"
            echo "$DIFFS"
            exit
        fi

    fi

#    XOUTFILE=${FILE}-x-yaml
#    if [ -f ${XOUTFILE} ]; then
#        ./parse_sudoers.py -f ${FILE} -a -x > $TMPFILE
#
#        DIFFS=$(diff -q $TMPFILE $XOUTFILE)
#    
#        if [ -z "$DIFFS" ]; then
#            echo "PASSED expanded $FILE"
#        else
#            echo "FAILED expanded $FILE"
#        fi
#
#    fi
done

