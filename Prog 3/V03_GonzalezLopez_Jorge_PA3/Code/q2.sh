#!/bin/bash

USAGE="Usage: ./q2.sh num_times num_nodes"

echo $USAGE


num_times=$1;
num_nodes=$2;


#Create 10 super peer nodes in an all-to-all topology

cd super_peers

cd super_peer_1
screen -d -m -S super_peer_1
sleep 0.1
screen -S super_peer_1 -X stuff 'python3 super_peer.py 127.0.0.1 3000 3001 3002 3003 3004 3005 3006 3007 3008 3009'$(echo -ne '\015')

cd ../super_peer_2
screen -d -m -S super_peer_2
sleep 0.1
screen -S super_peer_2 -X stuff 'python3 super_peer.py 127.0.0.1 3001 3000 3002 3003 3004 3005 3006 3007 3008 3009'$(echo -ne '\015')

cd ../super_peer_3
screen -d -m -S super_peer_3
sleep 0.1
screen -S super_peer_3 -X stuff 'python3 super_peer.py 127.0.0.1 3002 3000 3001 3003 3004 3005 3006 3007 3008 3009'$(echo -ne '\015')

cd ../super_peer_4
screen -d -m -S super_peer_4
sleep 0.1
screen -S super_peer_4 -X stuff 'python3 super_peer.py 127.0.0.1 3003 3000 3001 3002 3004 3005 3006 3007 3008 3009'$(echo -ne '\015')

cd ../super_peer_5
screen -d -m -S super_peer_5
sleep 0.1
screen -S super_peer_5 -X stuff 'python3 super_peer.py 127.0.0.1 3004 3000 3001 3002 3003 3005 3006 3007 3008 3009'$(echo -ne '\015')

cd ../super_peer_6
screen -d -m -S super_peer_6
sleep 0.1
screen -S super_peer_6 -X stuff 'python3 super_peer.py 127.0.0.1 3005 3000 3001 3002 3003 3004 3006 3007 3008 3009'$(echo -ne '\015')

cd ../super_peer_7
screen -d -m -S super_peer_7
sleep 0.1
screen -S super_peer_7 -X stuff 'python3 super_peer.py 127.0.0.1 3006 3000 3001 3002 3003 3004 3005 3007 3008 3009'$(echo -ne '\015')

cd ../super_peer_8
screen -d -m -S super_peer_8
sleep 0.1
screen -S super_peer_8 -X stuff 'python3 super_peer.py 127.0.0.1 3007 3000 3001 3002 3003 3004 3006 3006 3008 3009'$(echo -ne '\015')

cd ../super_peer_9
screen -d -m -S super_peer_9
sleep 0.1
screen -S super_peer_9 -X stuff 'python3 super_peer.py 127.0.0.1 3008 3000 3001 3002 3003 3004 3005 3006 3007 3009'$(echo -ne '\015')

cd ../super_peer_10
screen -d -m -S super_peer_10
sleep 0.1
screen -S super_peer_10 -X stuff 'python3 super_peer.py 127.0.0.1 3009 3000 3001 3002 3003 3004 3005 3006 3007 3008'$(echo -ne '\015')




#Wait until super peers are correctly deployed and connected
sleep 3


cd ../../weak_peers

#Deploy weak peer nodes
cd weak_peer_1
screen -d -m -S weak_peer_1
sleep 0.1
screen -S weak_peer_1 -X stuff 'python3 weak_peer.py 127.0.0.1 3000 all 6000 client_files'$(echo -ne '\015')


cd ../weak_peer_2
screen -d -m -S weak_peer_2
sleep 0.1
screen -S weak_peer_2 -X stuff 'python3 weak_peer.py 127.0.0.1 3001 all 6001 client_files'$(echo -ne '\015')


cd ../weak_peer_3
screen -d -m -S weak_peer_3
sleep 0.1
screen -S weak_peer_3 -X stuff 'python3 weak_peer.py 127.0.0.1 3002 all 6002 client_files'$(echo -ne '\015')

cd ../weak_peer_4
screen -d -m -S weak_peer_4
sleep 0.1
screen -S weak_peer_4 -X stuff 'python3 weak_peer.py 127.0.0.1 3003 all 6003 client_files'$(echo -ne '\015')

cd ../weak_peer_5
screen -d -m -S weak_peer_5
sleep 0.1
screen -S weak_peer_5 -X stuff 'python3 weak_peer.py 127.0.0.1 3004 all 6004 client_files'$(echo -ne '\015')

cd ../weak_peer_6
screen -d -m -S weak_peer_6
sleep 0.1
screen -S weak_peer_6 -X stuff 'python3 weak_peer.py 127.0.0.1 3005 all 6005 client_files'$(echo -ne '\015')

cd ../weak_peer_7
screen -d -m -S weak_peer_7
sleep 0.1
screen -S weak_peer_7 -X stuff 'python3 weak_peer.py 127.0.0.1 3006 all 6006 client_files'$(echo -ne '\015')

cd ../weak_peer_8
screen -d -m -S weak_peer_8
sleep 0.1
screen -S weak_peer_8 -X stuff 'python3 weak_peer.py 127.0.0.1 3007 all 6007 client_files'$(echo -ne '\015')

cd ../weak_peer_9
screen -d -m -S weak_peer_9
sleep 0.1
screen -S weak_peer_9 -X stuff 'python3 weak_peer.py 127.0.0.1 3008 all 6008 client_files'$(echo -ne '\015')

cd ../weak_peer_10
screen -d -m -S weak_peer_10
sleep 0.1
screen -S weak_peer_10 -X stuff 'python3 weak_peer.py 127.0.0.1 3009 all 6009 client_files'$(echo -ne '\015')


#Wait until weak peers are correctly deployed and registered
sleep 3

echo 'Start queries'

#Send queries simultaneously
for ((j=1;j<=num_times;j++));
do
	for ((i=1;i<=num_nodes;i++));
		do
			screen -S weak_peer_$i -X stuff 'query test1.txt'$(echo -ne '\015')
			echo 'Query sent'
			
		done
done

# After 5 seconds close all the sreens and terminate processes
sleep 5

pkill screen

