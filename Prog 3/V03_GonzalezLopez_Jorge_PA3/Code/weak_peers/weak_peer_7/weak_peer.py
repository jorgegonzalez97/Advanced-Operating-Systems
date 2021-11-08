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

#Arguments passed in the python command must be the right number
if len(sys.argv) == 6:
	S_H = sys.argv[1]
	S_P = int(sys.argv[2])
	topology = sys.argv[3]
	s_c_P = int(sys.argv[4])
	folder = sys.argv[5]
else:
	print('week_peer.py <IP_ADDRESS> <SUPER_PEER_PORT> <SUPER_PEER_TOPOLOGY> <SERVER_PORT> <FOLDER_NAME>')
	sys.exit(2)

#Buffer size for sending/receiving
BUFFER = 1024

#Configure log file
logging.basicConfig(filename="log.log",level=logging.INFO)


# Files pending for download
files_pending = {}

#TTL determined by the topology: TTL = 1 (all-to-all) and TTL = NUBER_SUPER_PEERS - 1 (linear)

TTL = 1

if topology == 'linear':
	TTL = 10 - 1


#Client socket
s = socket.socket()

#connecting to indexing server
s.connect((S_H, S_P))
print('\nConnected to SUPER PEER: ', S_H, ' : ', S_P)
logging.info('\nConnected to SUPER PEER: '+ str(S_H)+ ' : '+ str(S_P))

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
	#get list with all files in the folder
	files_list = os.listdir(os.getcwd()+"/"+folder)
	#convert list to a string
	listToStr = ' '.join([str(i) for i in files_list])
	#send the string 
	send_all(s,listToStr.encode())

#Function to send a file to another peer.
def send_file(file_encoded,conn,addr):
	
	#Receive name of file
	file = file_encoded.decode()
	
	# list with all files in the folder
	files_list = os.listdir(os.getcwd()+"/"+ folder)
	#Send an error message if file does not exist
	if file not in files_list:
		send_all(conn,'ERROR'.encode())
		#Wait confirmation from client
		logging.info('ERROR: File does not exist')
		data = recv_all(conn,BUFFER)
		return
	#Get the path of the file requested and its size
	path = os.getcwd()+"/"+folder+"/"+file 
	file_size = os.path.getsize(path)
	# Calculate hash of file
	file_content = open(path, "rb").read()

	md5_hash = hashlib.md5(file_content).hexdigest()
	#Send the name, size of the file and hash
	file_specs = str(file_size) + '<SEP>' + md5_hash

	send_all(conn,file_specs.encode())
	
	
	#Wait confirmation from client
	data = recv_all(conn,BUFFER)
	print(data.decode())
	logging.info(data.decode())

	#Get time before sending the file
	t = time.time()
	send_all(conn, file_content)
	t_down = time.time() - t
	#Save time spent sending the file
	print('\nFile ', file, '(',file_size,' bytes ) sent to client: ', addr, '. Time taken: ', t_down)
	logging.info('\nFile '+ file+ ' ('+str(file_size)+' bytes) sent to client: '+ str(addr)+ '. Time taken: '+ str(t_down))
	
	print('\nFile ', file, ' successfully sent to client: ', addr)
	logging.info('\nFile '+ file+ ' successfully sent to client: '+ str(addr))
	


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
		
			#Just for evaluation: save the time between query and all the queryhits.
			query_time = files_pending[str(request[1])][1]
			files_pending[str(request[1])][2] += (time.time() - query_time) 	# Save the sum of the times of all queryhits for every query
			files_pending[str(request[1])][3] += 1	   			# Save the total nnumber of queryhits for every query
			
			# Check if requested file has not been already download
			if files_pending[str(request[1])][0]:
				peer_nodes = re.findall(r'\[.*?\]', data.decode())
				#Select a node at random
				node = random.choice(peer_nodes)
				addr = re.findall(r'\'.*?\'', node)
				
				print('Downloading file from: ', addr)
				
				# File is not longer pending for download
				files_pending[str(request[1])][0] = False
				
				threading.Thread(target=download, args=(addr[0][1:-1],addr[1][1:-1], file_dow)).start()
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
def download(ip, port, file):
	#Client socket
	s_d = socket.socket()

	#connecting to client's server
	s_d.connect((ip, int(port)))
	print('\nConnected to peer: ', ip, ' : ', int(port))
	logging.info('\nConnected to peer : '+ ip + ' : '+ port)
	
	#Send name of file
	send_all(s_d,file.encode())	
	
	data = recv_all(s_d,BUFFER)
	#File specss
	file_spec = data.decode().split('<SEP>')
	
	#Check if file exists
	if file_spec[0] == 'ERROR':
		print('ERROR: File does not exist')
		logging.info('ERROR: File does not exist')
		#Tell server that it has been received
		send_all(s_d,'Error received'.encode())
		return
	
	#Answer server that it has been received
	send_all(s_d,'File specs received'.encode())
	
	#get path for download
	path = os.getcwd()+"/"+folder+"/"+file 
	
	t = time.time()
	#files written
	file_data = recv_all(s_d,int(file_spec[0]))

	#Get time taken to received the file
	t_down = time.time() - t

	#Write the data into the file
	with open(path,'wb') as f:
		f.write(file_data) 

	#Check the hash of the received file
	md5_hash = hashlib.md5(file_data).hexdigest()
	

	#Tell the client if the file received is fine
	if md5_hash == file_spec[1]:
		print('\nFile ', file,'(',file_spec[0],' bytes )', ' successfully downloaded. Time taken: ', t_down)
		logging.info('\nFile '+ file+' ('+file_spec[0]+' bytes )'+ ' successfully downloaded. Time taken: '+ str(t_down))
		send_all(s,'update'.encode())
		update_files_list()
	else:
		print('\nFile ', file, ' is corrupted')
		logging.info('\nFile '+ file+ ' is corrupted')
	
	s_d.close()
	
# Function to print the average time taken for all the queryhits of each query
def print_query_time(unique_id):
	
	# Cutoff time 0.5 seconds
	time.sleep(0.5)
	
	sum_times = files_pending[unique_id][2]
	n_queryhits = files_pending[unique_id][3]
	
	print('\n Number of queryhitsfor query '+ str(unique_id) + ': ' + str(n_queryhits))
	logging.info('\n Number of queryhitsfor query '+ str(unique_id) + ': ' + str(n_queryhits))
	
	#Only prints average time if there has been at least 1 queryhit
	if n_queryhits > 0:
		
		print('\n Average queryhit time: ' + str(sum_times/n_queryhits))
		logging.info('\n Average queryhit time: ' + str(sum_times/n_queryhits))


#One thread for the server (keep listening for possible connections)
threading.Thread(target=server, args=(s_c_P,)).start()


#Register for P2P downloads: Send the command register with the server port
complete_msg = 'register' + ' ' + str(s_c_P)
send_all(s,complete_msg.encode())
update_files_list()	
print('Registered for Peer-to-Peer downloads')
logging.info('Registered for Peer-to-Peer downloads')

#Main thread for client (write commands to super peer)
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
		message = message + ' ' + str(TTL) +' ' + str(unique_id) + ' ' + str(s_c_P)	
		
		
		initial_time = time.time()
		#Send the command download
		send_all(s,message.encode())
		
		# Save Flag to kow if file has already been download, the time the query was sent, ths sum of all the queryhits times and the total number of queryhits
		files_pending[str(unique_id)] = [True, initial_time, 0, 0]
		
		print('\n File: ' + file_dow + ' has been queried for download.')
		logging.info('\n File: ' + file_dow + ' has been queried for download.')
		
		#One thread to keep track of query times for evaluation
		threading.Thread(target=print_query_time, args=(str(unique_id),)).start()
		
		
	
	else:
		print('Command not supported')
		continue
