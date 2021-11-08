#!/bin/bash

USAGE="Usage: ./q2.sh "

echo $USAGE


for i in {0..3}; do
	echo "download serial t1.txt t2.txt t3.txt" | python3 client.py 127.0.0.1 3000 client_files &
done


