#!/bin/bash
BINDIR="$(cd `dirname $0` && pwd)"
PROJDIR="`dirname $BINDIR`"
DOWN_DIR="$HOME/Downloads"
AE_DIR="$PROJDIR/appengine"
AE_BIN="$AE_DIR/google_appengine"
ENV_DIR="$PROJDIR/gtugenv"

AE_FILES=http://googleappengine.googlecode.com/files
AE_VERSION="1.6.1"
PYTHON_CMD=python2.7
SETUP_TOOLS=setuptools-0.6c11-py2.7.egg

SUDO=sudo

if [ `uname` == "Darwin" ]; then
    platform="Mac"
elif [[ `uname` == *W32* ]]; then
    platform="Windows"
    SUDO=""
    PYTHON_VER="2.7.3"
    PYTHON_CMD=python2.7.exe
else
    platform="Linux"
fi

echo "I think your machine is running $platform ..."

# download <url> - do nothing if already downloaded
function download {
    FILE_PATH="$1"
    FILE="$( basename "$FILE_PATH" )"

    mkdir -p "$DOWN_DIR"
    if [ ! -f "$DOWN_DIR/$FILE" ]; then
        echo "Downloading $1"
        if ! curl "$FILE_PATH" --output "$DOWN_DIR/$FILE"; then
            echo "Failed to download $FILE_PATH"
            exit 1
        fi
    fi
}

# download_zip <url> <destination directory>
# download and unzip directory to destination
function download_zip {
    DEST_PATH="$2"

    download "$1"

    rm -rf "$DEST_PATH"
    mkdir "$DEST_PATH"
    unzip -q "$DOWN_DIR/$FILE" -d "$DEST_PATH"
}

function check_prog {
    type $1 > /dev/null 2>&1
}

cd "$PROJDIR"

if ! check_prog $PYTHON_CMD ; then
    echo "You need $PYTHON_CMD to use App Engine."
    if [ $platform == "Windows" ]; then
        download http://www.python.org/ftp/python/$PYTHON_VER/python-$PYTHON_VER.msi
        cd "$DOWN_DIR"
        msiexec -i $FILE
        ln -s /c/Python27/python.exe /c/Python27/python2.7.exe
        PATH=$PATH:/c/Python27:/c/Python27/Scripts
        export PATH
        echo 'PATH=$PATH:/c/Python27:/c/Python27/Scripts' >> "$HOME/.profile"
        cd "$PROJ_DIR"
    elif [ $platform == "Mac" ]; then
        echo "ERROR: Mac should already have $PYTHON_CMD installed."
        exit 1
    else
        sudo apt-get install python2.7
    fi
fi

if ! check_prog curl; then
    $SUDO apt-get install curl
fi

if ! check_prog easy_install ; then
    download http://pypi.python.org/packages/2.7/s/setuptools/$SETUP_TOOLS
    sudo sh "$DOWN_DIR/$SETUP_TOOLS"
fi

if ! check_prog pip ; then
    $SUDO easy_install pip
fi

if ! check_prog virtualenv ; then
    $SUDO pip install virtualenv
fi

read -p "Create local $PYTHON_CMD environment? (y/n): "
if [ "$REPLY" = "y" ]; then
    rm -rf "$ENV_DIR"
    virtualenv --python=$PYTHON_CMD "$ENV_DIR"
    if [ $platform = "Windows" ]; then
        ln -f -s "$ENV_DIR/Scripts/activate.bat"
    else
        ln -f -s "$ENV_DIR/bin/activate"
        source activate
    fi
    # pip install PIL
fi

read -p "Install App Engine ($AE_VERSION)? (y/n): "
if [ "$REPLY" = "y" ]; then
    if [ $platform == "Windows" ]; then
        download $AE_FILES/GoogleAppEngine-$AE_VERSION.msi
        cd "$DOWN_DIR"
        msiexec -i $FILE
        cd $PROJ_DIR
    elif [ $platform == "Mac" ]; then
        download "$AE_FILES/GoogleAppEngineLauncher-$AE_VERSION.dmg"
        open "$DOWN_DIR/$FILE"
    else
        rm -rf appengine
        download_zip "$AE_FILES/google_appengine_$AE_VERSION.zip" "$AE_DIR"
        ln -f -s $AE_BIN/*.py "$ENV_DIR/bin"
    fi
fi

if [ $platform == "Windows" ]; then
    echo "Open a Windows Command shell to use this environment."
    echo "And then type activate.bat"
else
    echo "Type 'source activate' to use this environment"
fi
