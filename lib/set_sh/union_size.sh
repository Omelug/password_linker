#!/bin/bash

# Arguments
TARGET_FILE=$1
OTHER_FILES=${@:2}

union_size=$(cat $TARGET_FILE $OTHER_FILES | sort | uniq | wc -l)

echo $union_size