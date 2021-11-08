#!/bin/bash

USAGE="Usage: ./q1.sh"

echo $USAGE

sleep 1


#Create three super peer nodes
cd super_peers

cd super_peer_1
screen -d -m -S super_peer_1
screen -S super_peer_1 -X stuff 'python3 super_peer.py 127.0.0.1 3000 3004 3008'$(echo -ne '\015')


cd ../super_peer_2
screen -d -m -S super_peer_2
screen -S super_peer_2 -X stuff 'python3 super_peer.py 127.0.0.1 3004 3000 3008'$(echo -ne '\015')


cd ../super_peer_3
screen -d -m -S super_peer_3
screen -S super_peer_3 -X stuff 'python3 super_peer.py 127.0.0.1 3008 3000 3004'$(echo -ne '\015')


#Wait until super peers are correctly deployed and connected
sleep 1

cd ../../weak_peers

#Deploy weak peer nodes
cd weak_peer_1
screen -d -m -S weak_peer_1
screen -S weak_peer_1 -X stuff 'python3 weak_peer.py 127.0.0.1 3000 all 6004 client_files'$(echo -ne '\015')


cd ../weak_peer_2
screen -d -m -S weak_peer_2
screen -S weak_peer_2 -X stuff 'python3 weak_peer.py 127.0.0.1 3004 all 6005 client_files'$(echo -ne '\015')


cd ../weak_peer_3
screen -d -m -S weak_peer_3
screen -S weak_peer_3 -X stuff 'python3 weak_peer.py 127.0.0.1 3008 all 6006 client_files'$(echo -ne '\015')

cd ../weak_peer_4
screen -d -m -S weak_peer_4
screen -S weak_peer_4 -X stuff 'python3 weak_peer.py 127.0.0.1 3000 all 6007 client_files'$(echo -ne '\015')


#Wait until weak peers are correctly deployed
sleep 2

#download simultaneously some files
screen -S weak_peer_1 -X stuff 'query test1.txt'$(echo -ne '\015')

echo 'First query done'

screen -S weak_peer_2 -X stuff 'query test2.txt'$(echo -ne '\015')

echo 'Second query done'

screen -S weak_peer_3 -X stuff 'query test3.txt'$(echo -ne '\015')

echo 'Third query done'

screen -S weak_peer_4 -X stuff 'query test4.txt'$(echo -ne '\015')

echo 'Fourth query done'







