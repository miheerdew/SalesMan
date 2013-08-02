#!/bin/bash
THIS_FILE=`readlink -f $0`
THIS_DIR=`dirname $THIS_FILE`
PROJECT_DIR=`dirname $THIS_DIR`
find $PROJECT_DIR -name '*.pyc' -exec rm '{}' \;
#rm -rf $PROJECT_DIR/build $PROJECT_DIR/dist
rm $PROJECT_DIR/log* &> /dev/null 
rm -rf $PROJECT_DIR/*.egg-info &> /dev/null
