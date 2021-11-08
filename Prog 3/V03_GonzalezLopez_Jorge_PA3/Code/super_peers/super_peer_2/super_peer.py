import socket
import hashlib
import os
import threading
import sys
import time
import logging

#Arguments passed in the python command must be the right number
if len(sys.argv) > 3:
	S_H = sys.argv[1]
	S_P = int(sys.argv[2])
	
	#Dictionary of super nodes: K - server port, V - socket or else: False
	super_nodes = {}
	
	for i in range(3, len(sys.argv)):
		super_nodes[sys.argv[i]] = False
	
else:
	print('super_peer.py <IP_ADDRESS> <OWN_PORT> <SUPER_NODES_PORTS>')
	sys.exit(2)

#Buffer size for sending/receiving
BUFFER = 1024

#Configure log file
logging.basicConfig(filename="log.log",level=logging.INFO)

#Information of nodes registered
reg_nodes = {}

#All weak nodes
weak_nodes = {}

#Information of files sent: key -> UID message, value -> previous server port
files_prop = {}

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


def queryhit_backprop(message, previous_server):
	# Get the connection of the super_node / weak_node and back prop queryhit:
	if str(previous_server) in super_nodes:
		socket = super_nodes[str(previous_server)]
		send_all(socket, message)
	elif str(previous_server) in weak_nodes:
		socket = weak_nodes[str(previous_server)]
		send_all(socket, message)

#Function to handle multiple weak nodes at the same time
def weak_node(conn, addr):

	while True:
		#receive command from client
		data = recv_all(conn,BUFFER)
		if data == b'':
			#If client is registered, unregister it.
			try:
				weak_nodes.pop(str(reg_nodes[str(addr)][0]))
				reg_nodes.pop(str(addr))
			except:
				pass
			print('Client',addr,' disconnected and unregistered.')
			logging.info('Client '+str(addr)+' disconnected and unregistered.')
			return

		#Get the command and arguments from the client request
		request = data.decode().split(' ')
		command = request[0]
		
		#Register client for P2P downloads
		if command == 'register':
			server_port = request[1]
			#Send confirmation message
			send_all(conn,'SEND FILES'.encode())
			#Receive files hosted
			data = recv_all(conn,BUFFER)
			#Register for Peer-to-Peer download
			reg_nodes[str(addr)] = [server_port,data.decode()]
			
			if str(server_port) not in weak_nodes:
				#Create client socket
				s_c = socket.socket()	
				s_c.connect((S_H, int(server_port)))
				#Register for Peer-to-Peer download
				weak_nodes[str(server_port)] = s_c
			
			print('Client: ', addr, ' registered.')
			logging.info('Client: '+str(addr)+' registered.')
		
		#Unregister client for P2P downloads (check if registered)
		elif command == 'unregister':
			try:
				reg_nodes.pop(str(addr))
				print('Client ',addr,' unregistered.')
				logging.info('Client '+str(addr)+' unregistered.')
			except:
				print('Client ',addr,' not registered.')
				logging.info('Client '+str(addr)+' not registered.')
		#Return all files hosted in all registered nodes
		elif command == 'get_files_list':
			#get all files from registerd nodes
			all_files = []
			for key, value in reg_nodes.items():
				#Only files from other peers
				if key != str(addr):
					val = value[1].split(' ')
					for v in val:
						#Not repeated files
						if v not in all_files:
							all_files.append(v)
			#convert list to a string

			listToStr = "\nFiles hosted: \n \n" + '\n'.join([str(i) for i in all_files])
		
			#send the string 
			conn.send(listToStr.encode())
			
			logging.info('Client '+str(addr)+' requested list of files.')
		#Update list after a client deletes a file
		elif command == 'delete':
			#Send confirmation message
			send_all(conn,'SEND FILES'.encode())
			#Receive files hosted
			data = recv_all(conn,BUFFER)
			if str(addr) in reg_nodes:
				#Register for Peer-to-Peer download
				reg_nodes[str(addr)][1] = data.decode()
				print('Client: ', addr, ' deleted a file.')
				logging.info('Client: '+str(addr)+' deleted a file.')
		#updates the list of files after downloading a file
		elif command == 'update':
			#Send confirmation message
			send_all(conn,'SEND FILES'.encode())
			#Receive files hosted
			data = recv_all(conn,BUFFER)
			if str(addr) in reg_nodes:
				#Register for Peer-to-Peer download
				reg_nodes[str(addr)][1] = data.decode()
				print('Client: ', addr, ' added a file.')
				logging.info('Client: '+str(addr)+' added a file.')
			
		#tell the clients the peers tha host the file requested	
		elif command == 'query':
		
			#get name of file, message uid and previous server port
			file_req = request[1]
			TTL = int(request[2])
			unique_id = request[3]
			previous_server = request[4]
			
			#Check if weak peer nodes host file requested
			peer_nodes = []
			for key, value in reg_nodes.items():
				if key != str(addr):
					val = value[1].split(' ')
					if (file_req in val):
						peer_nodes.append([key, value[0]])
			
			# Storage the previous server for back propagation
			files_prop[str(unique_id)] = previous_server
				 
			#convert list to a string
			if len(peer_nodes) > 0:
				listToStr = ' '.join([str(i) for i in peer_nodes])
				
				#Create queryhit message if at least one weak node hosts the file
				queryhit_message = 'queryhit' + ' ' + str(unique_id) + ' ' + listToStr
				
				#Send queryhit message
				queryhit_backprop(queryhit_message.encode(), previous_server)	
				
			if TTL > 0:
				TTL -= 1
				# Broadcast query message to all super nodes except for the one that sent it.
				for sn_port, sn_s in super_nodes.items():
					if sn_port != previous_server:
						query_message = 'query' + ' ' + file_req + ' ' + str(TTL) + ' ' + str(unique_id) + ' ' + str(S_P)
						send_all(sn_s, query_message.encode())
				
			#send the string 
			#conn.send(listToStr.encode())
			
			#logging.info('Client '+str(addr)+' requested to download file: '+str(file_req))
			
		elif command == 'queryhit':
			
			# Get UID for back propagation
			unique_id = request[1]
			
			# Get server port to send the message
			previous_server = files_prop[str(unique_id)]
			
			#Send queryhit message
			queryhit_backprop(data, previous_server)				
		
		else:
			continue



#Server socket
s = socket.socket()

#binding to local addres
s.bind((S_H, S_P))

#allow connections
s.listen()

print( 'Listening as ', S_H,' : ',S_P, '\n')
logging.info('Listening as '+ str(S_H)+ ' : '+ str(S_P) + '\n')


#Stablish connections with super nodes
for key, value in super_nodes.items():
	
	while True:
		#Create client socket
		s_c = socket.socket()
	
		try:
			s_c.connect((S_H, int(key)))
		except:
			#If connection failed, wait 1 us and try again.
			time.sleep(1e-6)
			continue
		
		#If connection worked, save the socket for future connections.
		super_nodes[key]= s_c
		break


while True:

	#accept connections
	conn, addr = s.accept()
	print('Client', addr,' connected to server. Total connections: ', threading.activeCount())
	logging.info('Client'+str(addr)+' connected to server.  Total connections: '+ str(threading.activeCount()))

	#One thread for each new connection
	threading.Thread(target=weak_node, args=(conn,addr)).start()







