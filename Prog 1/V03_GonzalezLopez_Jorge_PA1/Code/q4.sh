#!/bin/bash

USAGE="Usage: ./q4.sh  <File>"

echo $USAGE

#For loop that generates 4 concurrent clients which download 10 files in parallel (10 threads each). The File is an argument.

for ((i=0; i<4;i++)); do
	echo "download parallel $1 $1 $1 $1 $1 $1 $1 $1 $1 $1" | python3 client.py 127.0.0.1 3000 client_files &
done

