#!/bin/bash

# program to compile .cpp or .c file using opencv4

echo "compiling $1"
if [[ $1 == *.c ]]
then
    gcc -ggdb `pkg-config --cflags opencv` -o `basename $1 .c` $1 `pkg-config --libs opencv`;
elif [[ $1 == *.cpp ]]
then
	g++  `pkg-config --cflags opencv4` -o `basename $1 .cpp` $1 `pkg-config --libs opencv4`  -g -std=c++11 -ggdb;

else
    echo "Please compile only .c or .cpp files"
fi
echo "Output file => ${1%.*}"
