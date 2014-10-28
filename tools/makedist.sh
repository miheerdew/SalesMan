#!/bin/bash

set -e

usage(){
    cat <<__EOF__
    Usage: $0 [-wn]

    -w : Build windows exe. (in dist/Windows)
    -n : Build native executable (in dist/native)
__EOF__
}

build_windows(){
    echo "Building Windows"
    . VENV_WINE/bin/activate
    wine c:/Python27/python.exe ../pyinstaller/utils/build.py \
	--workpath=build/Windows \
	--distpath=dist/Windows \
	salesman.spec
    deactivate
}

build_native(){
    echo "Building native"
    . VENV/bin/activate
    ../pyinstaller/utils/build.py \
	--workpath=$ROOT_DIR/build/native \
	--distpath=$ROOT_DIR/dist/native \
    	salesman.spec
    deactivate
}

ROOT_DIR=$(dirname $(dirname $(readlink -f $0)))
WINDOWS=
NATIVE=

while getopts "wn" opt;do
    case $opt in
	w) WINDOWS=1
	    ;;
	n) NATIVE=1
	    ;;
       \?) usage
   	   exit
           ;;
	*) echo "Unexpected $opt"
    esac
done

cd "$ROOT_DIR"
[[ -z $WINDOWS ]] || build_windows
[[ -z $NATIVE ]] || build_native
