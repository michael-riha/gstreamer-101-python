#!/bin/bash

#if needed!
#apt-get install graphviz

INPUT_DIR="/opt/"

if [ -d "$INPUT_DIR" ]; then
    DOT_FILES=`find /opt/ -name "*.dot"`
    for file in $DOT_FILES
    do
        dest=`sed s/.dot/.pdf/ <<< "$file"`
        dot -Tpdf $file > $dest
    done
else
    echo "Input directory $INPUT_DIR does not exist"
fi