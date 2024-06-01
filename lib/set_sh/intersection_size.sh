#!/bin/bash

TARGET_FILE=$1
OTHER_FILE=$2

intersection_size=$(comm -12 <(sort $TARGET_FILE) <(sort $OTHER_FILE) | wc -l)

echo $intersection_size
