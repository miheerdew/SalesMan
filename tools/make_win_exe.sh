#!/bin/bash -e

if [ $# -ne 2 ]; then
    echo "Usage: $0 /path/to/main.py ProjectName"
    exit 1
else
    FULL_PY_PATH=`readlink -f $1`
    SOURCE_DIR_LINUX=`dirname ${FULL_PY_PATH}`
    MAIN_PY=`basename ${FULL_PY_PATH}`
    PROJECT_NAME="$2"
fi

THIS_SCRIPT_PATH=`readlink -f $0`
THIS_SCRIPT_DIR=`dirname ${THIS_SCRIPT_PATH}`

PYINSTALLER_ZIP=${THIS_SCRIPT_DIR}/build_environment/installers/pyinstaller-2.0.zip


PYTHON_EXE_WIN="C:\\Python27\\python.exe"

WINE_TARBALL=${THIS_SCRIPT_DIR}/build_environment/wine.tar.gz

if [ ! -e "${WINE_TARBALL}" ]; then
    echo "ERROR: You don't have a frozen wine environment at"
    echo "${WINE_TARBALL}"
    echo
    echo "Option 1:"
    echo "    Create a new wine environment by running build_environment/create.sh"
    echo "    and following the instructions."
    echo "Option 2:"
    echo "    Use an existing wine environment (with Python installed) by doing:"
    echo "    $ export WINEPREFIX=~/.wine    # path to your existing wine env"
    echo "    $ build_environment/freeze.sh"

    exit 2
else
    export WINEPREFIX=`mktemp -d --suffix=_wine`

    # Unpack wine environment
    tar "--directory=${WINEPREFIX}" -xzf ${WINE_TARBALL}

fi

BUILD_DIR_LINUX=${WINEPREFIX}/drive_c/build
BUILD_DIR_WIN="C:\\build"
mkdir -p ${BUILD_DIR_LINUX}


# Unpack PyInstaller
unzip ${PYINSTALLER_ZIP} -d ${BUILD_DIR_LINUX} > /dev/null
PYINSTALLER_DIR_WIN=${BUILD_DIR_WIN}\\pyinstaller-2.0

# Create symbolic link to source directory so Windows can access it
ln -s ${SOURCE_DIR_LINUX} ${BUILD_DIR_LINUX}/src_symlink
SOURCE_DIR_WIN=${BUILD_DIR_WIN}\\src_symlink

wine "${PYTHON_EXE_WIN}" "${PYINSTALLER_DIR_WIN}\\utils\\Makespec.py" \
    "--name=${PROJECT_NAME}" \
    --onefile \
    --noconsole \
    "--icon=${SOURCE_DIR_WIN}\\data\\AppIcon32x32.ico"\
    "--out=${BUILD_DIR_WIN}\\compiled" \
    "${SOURCE_DIR_WIN}\\${MAIN_PY}"

# patch to insert plugins dir

PLUGINS_DIR_WIN=${SOURCE_DIR_WIN}\\salesman\\plugins
PLUGINS_LINE="plugins=Tree(r'${PLUGINS_DIR_WIN}','plugins')"
ESCAPED_PLUGINS_LINE=$(echo "$PLUGINS_LINE"|sed 's|\\|\\\\|g')
SPECFILE="${BUILD_DIR_LINUX}/compiled/${PROJECT_NAME}.spec"

sed -i -e "/^exe = EXE(/ i\
${ESCAPED_PLUGINS_LINE}
"  -e "s/^exe = EXE(/&plugins,/ " ${SPECFILE}

# End patch
#geany ${SPECFILE}

wine "${PYTHON_EXE_WIN}" "${PYINSTALLER_DIR_WIN}\\utils\\Build.py"\
     "${BUILD_DIR_WIN}\\compiled\\${PROJECT_NAME}.spec"

mv "${BUILD_DIR_LINUX}/compiled/dist/${PROJECT_NAME}.exe" /tmp
rm -rf ${WINEPREFIX}

echo "Executable available at /tmp/${PROJECT_NAME}.exe"

