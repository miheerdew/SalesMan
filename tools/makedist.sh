#!/bin/bash
set -e


THIS_SCRIPT=$(readlink -f $0)
TOOLS_DIR=$(dirname $THIS_SCRIPT)
BASE_DIR=$(dirname "$TOOLS_DIR")
DIST_DIR_BASE=${BASE_DIR}/dist
APP_NAME=salesman
MAIN_PY=${BASE_DIR}/main.py

function usage(){
    cat <<_EOF
    $0 [options]

    Options

    -h          show this help
    -w          build windows Executable
    -n          build native executable
    -s          Do not build source dist

    Without any options nothing will be done
_EOF

}
###Make Windows Executable
function make_windows_exe(){
echo "Making windows executable"

WIN_DIST_DIR=${DIST_DIR_BASE}/windows
/bin/bash "${TOOLS_DIR}/make_win_exe.sh" "${MAIN_PY}" "${APP_NAME}"
mkdir -p "${WIN_DIST_DIR}"
mv "/tmp/${APP_NAME}.exe" "${WIN_DIST_DIR}"
echo "Windows Executable at ${WIN_DIST_DIR}/${APP_NAME}.exe"
}
##Make Distribution for the Current System

function make_executable(){
SAFE_OS_NAME=$(uname -o|sed 's|/|-|')
SAFE_PLATFORM_NAME=$(uname -i|sed 's|/|-|')
echo "Making executable for
OS:${SAFE_OS_NAME},
Platform:${SAFE_PLATFORM_NAME}"

DIST_DIR="${DIST_DIR_BASE}/${SAFE_OS_NAME}/${SAFE_PLATFORM_NAME}"
mkdir -p "${DIST_DIR}"
TMP_DIR=$(mktemp -d)
PYINSTALLER_ZIP=${TOOLS_DIR}/build_environment/installers/pyinstaller-2.0.zip
unzip ${PYINSTALLER_ZIP} -d ${TMP_DIR} > /dev/null
PYINSTALLER_DIR=${TMP_DIR}/pyinstaller-2.0
PYTHON_EXE=`which python2.7`
BUILD_DIR=${TMP_DIR}/build
WX_PATH=$(python2.7 -c 'import wxversion;wxversion.select("2.8");import sys;print sys.path[0]')
mkdir $BUILD_DIR
"$PYTHON_EXE" "$PYINSTALLER_DIR/utils/Makespec.py" \
    "--name=${APP_NAME}"\
    --onefile \
    --noconsole \
    "--paths=${WX_PATH}" \
    "--icon=${BASE_DIR}/data/AppIcon32x32.ico"\
    "--out=${BUILD_DIR}" \
    "${MAIN_PY}"

SPEC_FILE=${BUILD_DIR}/${APP_NAME}.spec

# patch to insert plugins dir


PLUGINS_DIR_WIN=${BASE_DIR}/salesman/plugins
PLUGINS_LINE="plugins=Tree(r'${PLUGINS_DIR_WIN}','plugins')"
ESCAPED_PLUGINS_LINE=$(echo "$PLUGINS_LINE"|sed 's|\\|\\\\|g')

sed -i -e "/^exe = EXE(/ i\
${ESCAPED_PLUGINS_LINE}
"  -e "s/^exe = EXE(/&plugins,/ " ${SPEC_FILE}

#geany ${SPEC_FILE}
# End patch

"${PYTHON_EXE}" "${PYINSTALLER_DIR}/utils/Build.py" "${SPEC_FILE}"
cp "${BUILD_DIR}/dist/${APP_NAME}" "${DIST_DIR}"

rm -rf ${TMP_DIR}
echo "Done. Executable Created at ${DIST_DIR}/${APP_NAME}"
}

function make_source_dist(){
 cd ${BASE_DIR}
 echo "Making Source Dist"
 python2.7 setup.py sdist
 echo "Done"
}

MAKE_WINDOWS=
MAKE_NATIVE=
MAKE_SOURCE=

while getopts "hwns" OPT
do
    case $OPT in
        h)
            usage
            exit 1
            ;;
        w)
            MAKE_WINDOWS=1
            ;;
        n)
            MAKE_NATIVE=1
            ;;
        s)
            MAKE_SOURCE=1
            ;;
        ?)
            usage
            exit -1
            ;;
    esac
done
echo .>log

[ -n "$MAKE_NATIVE" ] && make_executable
[ -n "$MAKE_WINDOWS" ] && make_windows_exe
[ -n "$MAKE_SOURCE" ] && make_source_dist
