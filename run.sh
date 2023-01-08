#!/bin/bash

echo
echo

if ! command -v python3 &> /dev/null;
then
    echo Python3 is not installed
    exit 1
fi

cd "$(dirname "$0")" || exit

if [ ! -d "venv" ];
then
    echo Creating virtual environment
    python3 -m venv venv

    . venv/bin/activate

    echo Installing dependencies
    command pip3 install -r requirements.txt --upgrade
else
    echo Activating virtual environment
    . venv/bin/activate
fi

if [ "$1" = "--install" ];
then
    shift
    echo Installing dependencies
    command pip3 install -r requirements.txt --upgrade
fi

echo Running main.py with args: "$@"
python3 main.py "$@"
