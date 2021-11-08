#!/bin/bash

USAGE="Usage: ./q2.sh <num_peers>"

echo $USAGE

cd server
screen -d -m -S server
screen -S server -X stuff 'python3 server.py 127.0.0.1 3000'$(echo -ne '\015')

# Wait till server is correctly deployed
sleep 3
echo 'Server deployed'

cd ../peers
#Create nodes

#Deploy clients
for ((i=1;i<=$1;i++));
	do
		port=400$i
		sleep 0.5
		screen -d -m -S peer_$i
		screen -S peer_$i -X stuff 'python3 peer.py 127.0.0.1 3000 '${port}' client_files_'$i' logs/log_'$i'.log'$(echo -ne '\015')
		sleep 0.5
		echo 'Peer deployed'
	done

# Wait till peers are correctly deployed
sleep 1

# Peer that will download the files
screen -d -m -S p_d
screen -S p_d -X stuff 'python3 peer.py 127.0.0.1 3000 5003 client_files_download logs/log_down.log'$(echo -ne '\015')

sleep 1		
echo 'All peers deployed'

#Download the 10 files from all the peers
for ((i=0;i<=10;i++));
	do
		sleep 0.5
		screen -S p_d -X stuff 'query '$i'.txt'$(echo -ne '\015')
		sleep 0.5
		echo 'File download'
	done



