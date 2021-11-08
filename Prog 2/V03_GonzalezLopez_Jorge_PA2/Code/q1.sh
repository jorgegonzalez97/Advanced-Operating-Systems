#!/bin/bash

USAGE="Usage: ./q1.sh "

echo $USAGE

#cd server
#screen -d -m -S server
#screen -S server -X stuff 'python3 server.py 127.0.0.1 3000'$(echo -ne '\015')

#Create nodes
cd client_3
screen -d -m -S client_3
screen -S client_3 -X stuff 'python3 client.py 127.0.0.1 3000 9456 client_files'$(echo -ne '\015')


cd ../client_2
screen -d -m -S client_2
screen -S client_2 -X stuff 'python3 client.py 127.0.0.1 3000 7456 client_files'$(echo -ne '\015')


cd ../client_1
screen -d -m -S client_1
screen -S client_1 -X stuff 'python3 client.py 127.0.0.1 3000 4456 client_files'$(echo -ne '\015')


cd ../client_4
screen -d -m -S client_4
screen -S client_4 -X stuff 'python3 client.py 127.0.0.1 3000 5546 client_files'$(echo -ne '\015')


sleep 1

#Register nodes
screen -S client_3 -X stuff 'register'$(echo -ne '\015')
screen -S client_2 -X stuff 'register'$(echo -ne '\015')
screen -S client_1 -X stuff 'register'$(echo -ne '\015')
screen -S client_4 -X stuff 'register'$(echo -ne '\015')

sleep 1

#download simultaneously some files 
screen -S client_1 -X stuff 'download test3.txt'$(echo -ne '\015')
screen -S client_2 -X stuff 'download test1.txt'$(echo -ne '\015')
screen -S client_3 -X stuff 'download test2.txt'$(echo -ne '\015')
screen -S client_1 -X stuff 'download test2.txt'$(echo -ne '\015')
screen -S client_4 -X stuff 'download test1.txt'$(echo -ne '\015')



