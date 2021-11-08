#!/bin/bash

USAGE="Usage: ./q3.sh  <N_clients>"

echo $USAGE

#For loop that generates N concurrent clients which download 10 files in parallel (10 threads each)

for ((i=0; i<$1;i++)); do
	echo "download parallel t1.txt t2.txt t3.txt t4.txt t5.txt t6.txt t7.txt t8.txt t9.txt t10.txt" | python3 client.py 127.0.0.1 3000 client_files &
done


