import socket
import hashlib
import os
import threading
import sys
import time
import logging
import random
import re 
import uuid
import math

#Arguments passed in the python command must be the right number
if len(sys.argv) == 6:
	S_H = sys.argv[1]
	S_P = int(sys.argv[2])
	s_c_P = int(sys.argv[3])
	folder = sys.argv[4]
	log_path = sys.argv[5]
else:
	print('client.py <IP_ADDRESS> <CLIENT_PORT> >SERVER_PORT> <FOLDER_NAME> <LOG_PATH>')
	sys.exit(2)

#Buffer size for sending/receiving
BUFFER = 1024

#Configure log file
logging.basicConfig(filename=log_path,level=logging.INFO)

# Files pending for download
files_pending = {}

#Client socket
s = socket.socket()

#connecting to indexing server
s.connect((S_H, S_P))
print('\nConnected to INDEXING SERVER: ', S_H, ' : ', S_P)
logging.info('\nConnected to INDEXING SERVER : '+ str(S_H)+ ' : '+ str(S_P))

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

#Function to tell the server the list of files the client hosts
def update_files_list():
	#Receive confirmation to send files
	data = recv_all(s,BUFFER)
	files_size_list = []
	#get list with all files in the folder
	files_list = os.listdir(os.getcwd()+"/"+folder)
	for file in files_list:
		#Get the path of the file requested and its size
		path = os.getcwd()+"/"+folder+"/"+file 
		file_size = os.path.getsize(path)
		files_size_list.append(file + '+' + str(file_size))
		
	#convert list to a string
	listToStr = ' '.join([str(i) for i in files_size_list])
	#send the string 
	send_all(s,listToStr.encode())

#Function to send a file to another peer.
def send_file(data, conn,addr):
	
	#[name, offst, chunk_size]
	file_down = data.decode().split(' ')
	
	offset = int(file_down[1])
	end_point = offset + int(file_down[2])
	
	# list with all files in the folder
	files_list = os.listdir(os.getcwd()+"/"+ folder)
	#Send an error message if file does not exist
	if file_down[0] not in files_list:
		send_all(conn,'ERROR'.encode())
		#Wait confirmation from client
		logging.info('ERROR: File does not exist')
		data = recv_all(conn,BUFFER)
		return
	
	#Get the path of the file requested
	path = os.getcwd()+"/"+folder+"/"+file_down[0] 
	
	#Get just the bytes of the chunk (from the offset received)
	file_content = open(path, "rb")
	file_send = file_content.read()[offset:end_point]
	
	print('Chunk size: ',file_down[2])
	print('Length of chunk to send: ',len(file_send))
	print('Position of the offset (beginning of chunk): ',offset)
	print('Position of the end (end of chunk): ',end_point)
	
	# Calculate hash of chunk
	md5_hash = hashlib.md5(file_send).hexdigest()
	
	#Send the name, size of the file chunk and hash
	file_specs = md5_hash

	send_all(conn,file_specs.encode())
	
	
	#Wait confirmation from client
	data = recv_all(conn,BUFFER)
	print(data.decode())
	logging.info(data.decode())


	send_all(conn, file_send)
	
	#Save time spent sending the file	
	print('Chunk sent to client ' + str(addr) + '. Size: ' + str(file_down[2]) + ' with offset: ' + str(offset))
	logging.info('Chunk sent to client ' + str(addr) + '. Size: ' + str(file_down[2]) + ' with offset: ' + str(offset))
	
	#conn.close()


def client_manager(conn,addr):
	
	while True:
		#receive command from client
		data = recv_all(conn,BUFFER)
		
		if data == b'':
			return

		#Get the command and arguments from the client request
		request = data.decode().split(' ')
		command = request[0]

		# Receive confirmation from queries
		if command == 'queryhit':
			
				
			peer_nodes = re.findall(r'\[.*?\]', data.decode())
			file_dow = files_pending[str(unique_id)][0]
			print('File: ', file_dow)
			file_size = int(request[2])
			print('File size: ', file_size)
			
			#Path to write the file once it gets downloaded
			path = os.getcwd()+"/"+folder+"/"+file_dow
			
			print('Peer nodes: ', peer_nodes)
			# Number of chunks == number of nodes that host the file
			number_chunks = len(peer_nodes)
			print('Number of peer nodes: ', number_chunks)
			chunk_size = int(math.floor(file_size/number_chunks))
			print('Chunk sizes: ', chunk_size)
			
			initial_time = time.time()
			
			threads = []
			for i in range(number_chunks):
			
				start_offset = i*chunk_size
				
				node = peer_nodes[i]
				
				addr = re.findall(r'\'.*?\'', node)
				
				print('Downloading Chunk ' + str(i) + ' from: ' + str(addr) + '. Size: ' + str(chunk_size) + ' with offset: ' + str(start_offset))
				logging.info('Downloading Chunk ' + str(i) + ' from: ' + str(addr) + '. Size: ' + str(chunk_size) + ' with offset: ' + str(start_offset))
				
				#list thread stores the port of the peers that have been asked for a chunk
				# ordered and the thread
				threads.append([addr[1][1:-1],threading.Thread(target=download, args=(addr[0][1:-1],addr[1][1:-1], file_dow, start_offset, chunk_size, str(request[1])))])
				
				threads[i][1].start()
		
			
			for t in threads:
				t[1].join()
			
			download_time = time.time() - initial_time	
			
			file_data = b''
			
			# Get the file by addign the chunks from the threads
			for i in range(number_chunks):
				file_data += files_pending[str(request[1])][1][threads[i][0]][0]
			
			if len(file_data) == file_size:
				#Write the data into the file
				with open(path,'wb') as f:
					f.write(file_data) 
				
				print('\nFile ' + file_dow + ' correctly downloaded from:\n')
				logging.info('\nFile ' + file_dow + ' correctly downloaded from:\n')
				
				
				for i in range(len(threads)):
					print('	--> Client ' + threads[i][0] + ' , chunk ' + str(i) + '. At time: ' + str(files_pending[str(request[1])][1][threads[i][0]][1]))
					logging.info('	--> Client ' + threads[i][0] + ' , chunk ' + str(i) + '. At time: ' + str(files_pending[str(request[1])][1][threads[i][0]][1]))
				
				print('\nTotal time to download all the chunks: ' + str(download_time) + ' sec.')
				logging.info('\nTotal time to download all the chunks: ' + str(download_time) + ' sec.')
				
				send_all(s,'update'.encode())
				update_files_list()
			else:
				print('\nFile ' + file_dow + ' download failed.\n')
				logging.info('\nFile ' + file_dow + ' download failed.\n')
	
	
		# Download connection from weak node
		else:
			print('Sending file to: ', addr)
			send_file(data,conn,addr)


#Function call by a thread that creates a server and keeps listening for upcoming connections
def server(server_port):

	#Server socket
	server = socket.socket()

	#binding to local addres
	server.bind((S_H, server_port))

	#allow connections
	server.listen()

	print( 'Listening as ', S_H,' : ',server_port, '\n')
	logging.info('Listening as '+ str(S_H)+ ' : '+ str(server_port) + '\n')
	
	while True:
		
		#accept connections
		conn, addr = server.accept()
		print('Client', addr,' connected. Total connections: ', threading.activeCount())
		logging.info('Client'+str(addr)+' connected.  Total connections: '+ str(threading.activeCount()))

		#One thread for each new connection
		threading.Thread(target=client_manager, args=(conn,addr)).start()
		
#Function to download file from another peer		
def download(ip, port, file, start_offset, chunk_size, file_uid):
	#Client socket
	s_d = socket.socket()

	#connecting to client's server
	s_d.connect((ip, int(port)))
	print('\nConnected to peer: ', ip, ' : ', int(port))
	logging.info('\nConnected to peer : '+ ip + ' : '+ port)
	
	#Send name of file, offset and chunk size
	msg = file + ' ' + str(start_offset) + ' ' + str(chunk_size)
	send_all(s_d,msg.encode())	
	
	data = recv_all(s_d,BUFFER)
	
	#File specss
	hash_origin = data.decode()
	
	#Check if file exists
	if hash_origin == 'ERROR':
		print('ERROR: File does not exist')
		logging.info('ERROR: File does not exist')
		#Tell server that it has been received
		send_all(s_d,'Error received'.encode())
		return
	
	#Answer server that it has been received
	send_all(s_d,'File specs received'.encode())
	
	t = time.time()
	
	#files written
	file_data = recv_all(s_d,int(chunk_size))
	
	
	# save client to which the file is asked
	files_pending[file_uid][1][port] = [file_data, t] 

	#Check the hash of the chunk
	md5_hash = hashlib.md5(file_data).hexdigest()
	

	#Tell the client if the file received is fine
	if md5_hash == hash_origin:
		print('\nChunk from client ' + port + ' of file '+ file + ' has been correctly downloaded. Length: ' + str(chunk_size) + ' , with offset: '+ str(start_offset))
		logging.info('\nChunk from client ' + port + ' of file '+ file + ' has been correctly downloaded. Length: ' + str(chunk_size) + ' , with offset: '+ str(start_offset))

	else:
		print('\nChunk from client ' + port + ' of file'+ file + ' is corrupted. Length: ' + str(chunk_size) + 'with offset: '+ str(start_offset))
		logging.info('\nChunk from client ' + port + ' of file'+ file + ' is corrupted. Length: ' + str(chunk_size) + 'with offset: '+ str(start_offset))
	
	s_d.close()





#One thread for the server (keep listening for possible connections)
threading.Thread(target=server, args=(s_c_P,)).start()

#Register for P2P downloads: Send the command register with the server port
complete_msg = 'register' + ' ' + str(s_c_P)
send_all(s,complete_msg.encode())
update_files_list()	
print('Registered for Peer-to-Peer downloads')
logging.info('Registered for Peer-to-Peer downloads')

#Main thread for client (write commands to indexing server)
while True:

	#Wrtte message in the command line
	message = input()

	
	if message == '':
		continue
		
	#Split the message in words
	m = message.split(' ')
	command = m[0]
	
	#register -> for peer download
	if command == 'register':
		#Send the command register with the server port
		complete_msg = message + ' ' + str(s_c_P)
		send_all(s,complete_msg.encode())
		update_files_list()
			
		print('Registered for Peer-to-Peer downloads')
		logging.info('Registered for Peer-to-Peer downloads')
	#unregister -> for peer download
	elif command == 'unregister':
		#Send the command unregister
		send_all(s,message.encode())
		print('Unregistered for Peer-to-Peer downloads')
		logging.info('Unregistered for Peer-to-Peer downloads')
	#get all files that are avilable in all the registered nodes
	elif command == 'get_files_list':
		#Send the command get_files_list
		send_all(s,message.encode())
		#Receive answer from server
		data = recv_all(s,BUFFER)
		#print answer
		print(data.decode())
	#delete file from own folder and update list of files in server
	elif command == 'delete':
		# list with all files in the folder
		files_list = os.listdir(os.getcwd()+"/"+folder)
		file_del = m[1]
		#Send an error message if file does not exist
		if file_del not in files_list:
			print('ERROR :  File does not exist.')
		else:
			#Get the path of the file requested
			path = os.getcwd()+"/"+folder+"/"+file_del
			#Delete file
			os.remove(path)
			print('\nFile ', file_del , ' deleted.')
			#Send the command download
			send_all(s,message.encode())
			update_files_list()
			
	#download file from another peer			
	elif command == 'query':
		
		file_dow = m[1]
		
		#Generate a random UUID
		unique_id = uuid.uuid4()
		
		#Add unique_id ans servers port to the message
		message = message + ' ' + str(unique_id) + ' ' + str(s_c_P)	
		
		#Send the command download
		send_all(s,message.encode())
		
		# Save Flag to kow if file has already been download
		files_pending[str(unique_id)] = [file_dow, {}]
		
		print('\n File: ' + file_dow + ' has been queried for download.')
		logging.info('\n File: ' + file_dow + ' has been queried for download.')
		
	
	else:
		print('Command not supported')
		continue
