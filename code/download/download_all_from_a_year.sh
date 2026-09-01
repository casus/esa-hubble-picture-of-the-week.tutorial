#!/bin/bash

if [ $# -eq 0 ]; then

    echo "need to specify a year after 2010 as 2 digits >= 10 and <= 25"
    exit 1
fi

HOST="https://esahubble.org"
BASE="${HOST}/images/"

YEAR=$1
echo
echo "# download all from year $YEAR"
echo 

for WEEK in `seq -w 01 55`; do 

    echo
    echo "    # year $YEAR week $WEEK"
    echo 

    DIR="${YEAR}__/${YEAR}${WEEK}/"
    mkdir -p $DIR
    FILE="potw${YEAR}${WEEK}a"
    echo curl -o ${DIR}${FILE} ${BASE}${FILE}/
    curl -o ${DIR}${FILE} ${BASE}${FILE}/ || continue

    if grep -q "Page not found" ${DIR}${FILE} ; then

        echo "    not found, abort"
        rm ${DIR}${FILE}
        rmdir ${DIR}
        break
    fi

    datalad save -m "Add $YEAR$WEEK" $DIR

    # tif
    TIFURL=`cat ${DIR}${FILE} | grep 'Fullsize Original' | grep -oP 'href="\K[^"]+'`
    if [[ "$TIFURL" == https://* ]]; then
        # URL good
        TIFURL=$TIFURL
    elif [[ "$TIFURL" == http://* ]]; then
        # URL good
        TIFURL=$TIFURL
    else
        TIFURL=$HOST$TIFURL
    fi

    # jpg
    JPGURL=`cat ${DIR}${FILE} | grep 'Large JPEG' | grep -oP 'href="\K[^"]+'`
    if [[ "$JPGURL" == https://* ]]; then
        # URL good
        JPGURL=$JPGURL
    elif [[ "$JPGURL" == http://* ]]; then
        # URL good
        JPGURL=$JPGURL
    else
        JPGURL=$HOST$JPGURL
    fi

    cd ${DIR}
    datalad download-url $TIFURL $JPGURL
    cd ../../

    datalad run -m "Metadata for $YEAR$WEEK" \
        -i ${DIR}${FILE} \
        ./code/metadata/extract_metadata.py $DIR -r

    sleep 1
    echo 
    echo

done