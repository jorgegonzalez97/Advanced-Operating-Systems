#!/bin/bash

USAGE="Usage: ./s.sh "

echo $USAGE

cd server
python3 server.py 127.0.0.1 3000

