import socket
import hashlib
import os
import threading
import sys
import time

#Arguments passed in the python command must be the right number
if len(sys.argv) == 4:
	S_H = sys.argv[1]
	S_P = int(sys.argv[2])
	folder = sys.argv[3]
else:
	print('client.py <IP_ADDRESS> <PORT> <FOLDER_NAME>')
	sys.exit(2)

#Buffer size for sending/receiving
BUFFER = 1024

#Client socket
s = socket.socket()

#connecting to server
s.connect((S_H, S_P))
print('\nConnected to: ', S_H, ' : ', S_P)

#Function for every time data is sent to client: loop to make sure 
#all the data is sent.
def send_all(conn, data):
	tosend = len(data)
	sent = 0
	while sent < tosend:
		to_read = min(BUFFER, tosend - sent)
		sent+= conn.send(data[sent:sent + to_read])

#Function for every time data is received from client: loop to make sure 
#all the data is received.
def recv_all(conn, to_receive):
	received = 0
	total_data = b''
	while received < to_receive:
		data = conn.recv(BUFFER)
		received += len(data)
		total_data += data
		if len(data) < BUFFER:
			break
	return total_data

#Function used to receive file ask by client
def receive_files(s,file):

	data = recv_all(s,BUFFER)
	#File specss
	file_spec = data.decode().split('<SEP>')
	
	#Answer server that it has been received
	send_all(s,'File specs received'.encode())
	
	#Check if file exists
	if file_spec[0] == 'ERROR':
		print('ERROR: File does not exist')
		#Tell server that it has been received
		send_all(s,'Error received'.encode())
		return
	
	#get path for download
	path = os.getcwd()+"/"+folder+"/"+file 
	
	t = time.time()
	#files written
	file_data = recv_all(s,int(file_spec[0]))

	#Get time taken to received the file
	t_down = time.time() - t

	#Write the data into the file
	with open(path,'wb') as f:
		f.write(file_data) 

	#Check the hash of the received file
	md5_hash = hashlib.md5(file_data).hexdigest()

	#Tell the client if the file received is fine
	if md5_hash == file_spec[1]:
		print('\nFile ', file, ' successfully downloaded. Time taken: ', t_down)
	else:
		print('\nFile ', file, ' is corrupted')
	
	#Tell server that it has been received
	send_all(s,'File received'.encode())

#Function used to add a file to the server
def send(file):
	# list with all files in the folder
	files_list = os.listdir(os.getcwd()+"/"+folder)
	#Send an error message if file does not exist
	if file not in files_list:
		print('ERROR :  File does not exist.')
		return
	#Get the path of the file requested and its size
	path = os.getcwd()+"/"+folder+"/"+file 
	file_size = os.path.getsize(path)
	#Send the name and the size of the file
	file_specs = '\nFile requested: ' + file + ', with size: '+ str(file_size)
	send_all(s,file_specs.encode())
	
	#Wait confirmation from client
	data = recv_all(s,BUFFER)
	
	#Send file
	filecontent = open(path,'rb').read()
	send_all(s,filecontent)
	
	#Wait confirmation from client
	data = recv_all(s,BUFFER)
	
	print('\nFile ', file, ' successfully added')

def parallel_receiving(file,files_received):
	#Create and connect a Client socket for every file
	s_t = socket.socket()
	s_t.connect((S_H, S_P))
	#Send the request
	mess_t = 'download parallel '+ file
	send_all(s_t,mess_t.encode())
	#download file
	receive_files(s_t,file)
	files_received.append(file)
	s_t.close()


while True:
	#Wrtte message in the command line
	try:
		message = input()
	except EOFError:
		s.close()
		sys.exit(2)
	
	if message == '':
		continue
	#Split the message in words
	m = message.split(' ')
	command = m[0]
	
	#Check the command 
	if command == 'download':
		#See if serial or parallel download has been requested
		if len(m) > 1 and m[1] == 'serial':
			#Send command
			send_all(s,message.encode())
			#Get time before staritn receiving
			t_total = time.time()
			#Receive each file one after another and record total time
			for i in range(2,len(m)):
				#Get the name of the file
				file = m[i]
				#download file
				receive_files(s,file)
			print('\nFinish downloading. Total time (with communication and comprobations): ', time.time() - t_total)
		elif len(m) > 1 and m[1] == 'parallel':
			#Create a temporal new connection for every file, received and close connection.
			files_received = []
			t_total = time.time()
			for i in range(2,len(m)):
				#Get the name of the file
				file = m[i]
				#One thread for each new file
				threading.Thread(target=parallel_receiving, args=(file,files_received)).start()
			while True:
				if len(files_received) == len(m)-2:
					print('\nFinish downloading. Total time (with communication and comprobations): ', time.time() - t_total)
					break
		else:
			print('\n Type of download either serial or parallel')
	elif command == 'add':
		#Send command
		send_all(s,message.encode())
		#get name of file
		file = m[1]
		# Add a new file in server
		send(file)
	elif command == 'close':
		s.close()
		sys.exit(2)
	else:
		#For the rest of commands, send it.
		send_all(s,message.encode())
		#Receive answer from server
		data = recv_all(s,BUFFER)
		#print answer
		print(data.decode())
