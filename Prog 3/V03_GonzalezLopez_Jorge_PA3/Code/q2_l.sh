#!/bin/bash

USAGE="Usage: ./q2_l.sh num_times num_nodes"

echo $USAGE


num_times=$1;
num_nodes=$2;


#Create 10 super peer nodes in a serial topology

cd super_peers

cd super_peer_1
screen -d -m -S super_peer_1
sleep 0.1
screen -S super_peer_1 -X stuff 'python3 super_peer.py 127.0.0.1 3000 3001'$(echo -ne '\015')

cd ../super_peer_2
screen -d -m -S super_peer_2
sleep 0.1
screen -S super_peer_2 -X stuff 'python3 super_peer.py 127.0.0.1 3001 3000 3002'$(echo -ne '\015')

cd ../super_peer_3
screen -d -m -S super_peer_3
sleep 0.1
screen -S super_peer_3 -X stuff 'python3 super_peer.py 127.0.0.1 3002 3001 3003 '$(echo -ne '\015')

cd ../super_peer_4
screen -d -m -S super_peer_4
sleep 0.1
screen -S super_peer_4 -X stuff 'python3 super_peer.py 127.0.0.1 3003 3002 3004'$(echo -ne '\015')

cd ../super_peer_5
screen -d -m -S super_peer_5
sleep 0.1
screen -S super_peer_5 -X stuff 'python3 super_peer.py 127.0.0.1 3004 3003 3005'$(echo -ne '\015')

cd ../super_peer_6
screen -d -m -S super_peer_6
sleep 0.1
screen -S super_peer_6 -X stuff 'python3 super_peer.py 127.0.0.1 3005 3004 3006'$(echo -ne '\015')

cd ../super_peer_7
screen -d -m -S super_peer_7
sleep 0.1
screen -S super_peer_7 -X stuff 'python3 super_peer.py 127.0.0.1 3006 3005 3007'$(echo -ne '\015')

cd ../super_peer_8
screen -d -m -S super_peer_8
sleep 0.1
screen -S super_peer_8 -X stuff 'python3 super_peer.py 127.0.0.1 3007 3006 3008'$(echo -ne '\015')

cd ../super_peer_9
screen -d -m -S super_peer_9
sleep 0.1
screen -S super_peer_9 -X stuff 'python3 super_peer.py 127.0.0.1 3008 3007 3009'$(echo -ne '\015')

cd ../super_peer_10
screen -d -m -S super_peer_10
sleep 0.1
screen -S super_peer_10 -X stuff 'python3 super_peer.py 127.0.0.1 3009 3008'$(echo -ne '\015')




#Wait until super peers are correctly deployed and connected
sleep 3


cd ../../weak_peers

#Deploy weak peer nodes
cd weak_peer_1
screen -d -m -S weak_peer_1
sleep 0.1
screen -S weak_peer_1 -X stuff 'python3 weak_peer.py 127.0.0.1 3000 linear 6000 client_files'$(echo -ne '\015')


cd ../weak_peer_2
screen -d -m -S weak_peer_2
sleep 0.1
screen -S weak_peer_2 -X stuff 'python3 weak_peer.py 127.0.0.1 3001 linear 6001 client_files'$(echo -ne '\015')


cd ../weak_peer_3
screen -d -m -S weak_peer_3
sleep 0.1
screen -S weak_peer_3 -X stuff 'python3 weak_peer.py 127.0.0.1 3002 linear 6002 client_files'$(echo -ne '\015')

cd ../weak_peer_4
screen -d -m -S weak_peer_4
sleep 0.1
screen -S weak_peer_4 -X stuff 'python3 weak_peer.py 127.0.0.1 3003 linear 6003 client_files'$(echo -ne '\015')

cd ../weak_peer_5
screen -d -m -S weak_peer_5
sleep 0.1
screen -S weak_peer_5 -X stuff 'python3 weak_peer.py 127.0.0.1 3004 linear 6004 client_files'$(echo -ne '\015')

cd ../weak_peer_6
screen -d -m -S weak_peer_6
sleep 0.1
screen -S weak_peer_6 -X stuff 'python3 weak_peer.py 127.0.0.1 3005 linear 6005 client_files'$(echo -ne '\015')

cd ../weak_peer_7
screen -d -m -S weak_peer_7
sleep 0.1
screen -S weak_peer_7 -X stuff 'python3 weak_peer.py 127.0.0.1 3006 linear 6006 client_files'$(echo -ne '\015')

cd ../weak_peer_8
screen -d -m -S weak_peer_8
sleep 0.1
screen -S weak_peer_8 -X stuff 'python3 weak_peer.py 127.0.0.1 3007 linear 6007 client_files'$(echo -ne '\015')

cd ../weak_peer_9
screen -d -m -S weak_peer_9
sleep 0.1
screen -S weak_peer_9 -X stuff 'python3 weak_peer.py 127.0.0.1 3008 linear 6008 client_files'$(echo -ne '\015')

cd ../weak_peer_10
screen -d -m -S weak_peer_10
sleep 0.1
screen -S weak_peer_10 -X stuff 'python3 weak_peer.py 127.0.0.1 3009 linear 6009 client_files'$(echo -ne '\015')


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

