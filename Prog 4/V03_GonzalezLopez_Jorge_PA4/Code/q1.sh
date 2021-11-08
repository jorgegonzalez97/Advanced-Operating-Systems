#!/bin/bash

USAGE="Usage: ./q1.sh "

echo $USAGE

cd server
screen -d -m -S server
screen -S server -X stuff 'python3 server.py 127.0.0.1 3000'$(echo -ne '\015')

# Wait till server is correctly deployed
sleep 5

cd ../peers
#Create nodes

screen -d -m -S peer_1
screen -S peer_1 -X stuff 'python3 peer.py 127.0.0.1 3000 4000 client_files_1 logs/log_1.log'$(echo -ne '\015')

sleep 1

screen -d -m -S peer_2
screen -S peer_2 -X stuff 'python3 peer.py 127.0.0.1 3000 4010 client_files_2 logs/log_2.log'$(echo -ne '\015')

sleep 1

screen -d -m -S peer_3
screen -S peer_3 -X stuff 'python3 peer.py 127.0.0.1 3000 4020 client_files_3 logs/log_3.log'$(echo -ne '\015')

sleep 1

screen -d -m -S peer_4
screen -S peer_4 -X stuff 'python3 peer.py 127.0.0.1 3000 4030 client_files_4 logs/log_4.log'$(echo -ne '\015')

sleep 1

screen -d -m -S peer_5
screen -S peer_5 -X stuff 'python3 peer.py 127.0.0.1 3000 4040 client_files_5 logs/log_5.log'$(echo -ne '\015')

# Wait till peers are correctly deployed
sleep 5


#download simultaneously some files 
screen -S peer_1 -X stuff 'query 1.txt'$(echo -ne '\015')
screen -S peer_2 -X stuff 'query 2.txt'$(echo -ne '\015')
screen -S peer_3 -X stuff 'query 3.txt'$(echo -ne '\015')
screen -S peer_4 -X stuff 'query 4.txt'$(echo -ne '\015')
screen -S peer_5 -X stuff 'query 5.txt'$(echo -ne '\015')



