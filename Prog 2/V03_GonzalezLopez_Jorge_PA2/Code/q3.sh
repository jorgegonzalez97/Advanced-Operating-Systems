#!/bin/bash

USAGE="Usage: ./q3.sh file num_times"

echo $USAGE

cd server

sleep 1

#Create nodes
num_peers=4;
file=$1;
num_times=$2;

#Deploy clients
for ((i=1;i<=num_peers;i++));
	do
		cd ../client_$i
		port=652$i
		screen -d -m -S client_$i
		screen -S client_$i -X stuff 'python3 client.py 127.0.0.1 3000 '${port}' client_files'$(echo -ne '\015')
		
	done

#Wait until clients are correctly deployed
sleep 1

#Register nodes
#Deploy clients
for ((i=1;i<=num_peers;i++));
	do
		screen -S client_$i -X stuff 'register'$(echo -ne '\015')
		
	done

#Wait until clients are correctly registered
sleep 1

#download simultaneously the file <FILE>, <NUM_TIMES> times
for ((j=1;j<=num_times;j++));
do
	for ((i=1;i<=num_peers;i++));
		do
			screen -S client_$i -X stuff 'download '${file}$(echo -ne '\015')
		
		done
done



