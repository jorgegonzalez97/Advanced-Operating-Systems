import socket
import hashlib
import os
import threading
import sys
import time
import logging

#Arguments passed in the python command must be the right number
if len(sys.argv) == 4:
	S_H = sys.argv[1]
	S_P = int(sys.argv[2])
	folder = sys.argv[3]
else:
	print('server.py <IP_ADDRESS> <PORT> <FOLDER_NAME>')
	sys.exit(2)

#Buffer size for sending/receiving
BUFFER = 1024

#Configure log file
logging.basicConfig(filename="../Out/log.log",level=logging.INFO)

#Server socket
s = socket.socket()

#binding to local addres
s.bind((S_H, S_P))

#allow connections
s.listen()

print( 'Listening as ', S_H,' : ',S_P, '\n')
logging.info('Listening as '+ str(S_H)+ ' : '+ str(S_P) + '\n')

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

#Function used when the client ask for an specific file
def download(conn, addr, file):
	# list with all files in the folder
	files_list = os.listdir(os.getcwd()+"/"+ folder)
	#Send an error message if file does not exist
	if file not in files_list:
		send_all(conn,'ERROR'.encode())
		#Wait confirmation from client
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

	#Get time spent before sending the file
	t = time.time()
	send_all(conn, file_content)
	t_down = time.time() - t
	#Save time spent sending the file
	print('\nFile ', file, '(',file_size,' bytes ) sent to client: ', addr, '. Time taken: ', t_down)
	logging.info('\nFile '+ file+ ' ('+str(file_size)+' bytes) sent to client: '+ str(addr)+ '. Time taken: '+ str(t_down))
	
	#Wait confirmation from client
	data = recv_all(conn,BUFFER)
	print(data.decode())
	logging.info(data.decode())

#Function used when the client wants to delete a file
def delete(conn,file):
	# list with all files in the folder
	files_list = os.listdir(os.getcwd()+"/"+folder)
	#Send an error message if file does not exist
	if file not in files_list:
		conn.send('ERROR :  File does not exist.'.encode())
		return
	else:
		#Get the path of the file requested
		path = os.getcwd()+"/"+folder+"/"+file
		#Delete file
		os.remove(path)
		msg = '\nFile '+ file + ' deleted.'
		send_all(conn,msg.encode())

#Function used when the client wants to modify the name of a file
def modify(conn,file, new_name):
	# list with all files in the folder
	files_list = os.listdir(os.getcwd()+"/"+folder)
	#Send an error message if file does not exist
	if file not in files_list:
		send_all(conn,'ERROR :  File does not exist.'.encode())
		return
	else:
		#Get the path of the file requested 
		path = os.getcwd()+"/"+folder+"/"+file
		#Get path with new name 
		new_path = os.getcwd()+"/"+folder+"/"+new_name
		#rename file
		os.rename(path,new_path)
		msg = '\nFile '+ file + ' is now called: ' + new_name
		send_all(conn,msg.encode())

#Function used when the client wants to add a file
def add(conn,file):
	data = recv_all(conn, BUFFER)
	file_spec = data.decode().split(' ')
	print(data.decode())
	logging.info(data.decode())
	
	#Answer server that it has been received
	send_all(conn,'File specs received'.encode())

	#get path for download
	path = os.getcwd()+"/"+folder+"/"+file 
	#add file
	filecontent = recv_all(conn,int(file_spec[-1]))
	
	with open(path,'wb') as f:
		f.write(filecontent)
	
	#Answer server that it has been received
	send_all(conn,'OK'.encode())
	
	print('\nFile ', file, ' successfully added')
	logging.info('\nFile ' + file + ' successfully added')

#Function to handle multiple clients at the same time
def client_manager(conn, addr):

	while True:
		#receive command from client
		data = conn.recv(BUFFER)
		if data == b'':
			print('Client',addr,' disconnected.')
			logging.info('Client'+str(addr)+'disconnected.')
			return

		#Get the command and arguments from the client request
		request = data.decode().split(' ')
		command = request[0]

		if command == 'get_files_list':
			#get list with all files in the folder
			files_list = os.listdir(os.getcwd()+"/"+folder)
			#convert list to a string
			listToStr = "\nFiles hosted: \n \n"+'\n'.join([str(i) for i in files_list])
			#send the string 
			conn.send(listToStr.encode())
		elif command == 'add':
			#Get file name and call fucntion to add it
			file = request[1]
			add(conn,file)
		elif command == 'modify':
			#Get file name, new name and call fucntion to modify it
			file = request[1]
			new_name = request[2]
			#change file name to new_name
			modify(conn,file,new_name)
		elif command == 'delete':
			#Get file name and call function to delete it
			file = request[1]
			#delete the file
			delete(conn,file)
		elif command == 'download':
			#See if serial or parallel download has been requested
			if request[1] == 'serial':
				#Download each file one after another and record total time
				t_total = time.time()
				for i in range(2,len(request)):
					#Get the file requested
					file = request[i]
					#download file
					download(conn, addr, file)
				print('\nFinish Sending. Total time: ', time.time() - t_total)
				logging.info('\nFinish Sending. Total time: '+ str(time.time() - t_total))
			elif request[1] == 'parallel':
				#Client will create one connection for every different file.
				file = request[2]
				download(conn, addr, file)
			else:
				#Only serial and parallel type of downloads supported
				continue
			
		else:
			conn.send("\nCommand not supported... yet".encode())


while True:

	#accept connections
	conn, addr = s.accept()
	print('Client', addr,' connected to server. Total connections: ', threading.activeCount())
	logging.info('Client'+str(addr)+' connected to server.  Total connections: '+ str(threading.activeCount()))

	#One thread for each new connection
	threading.Thread(target=client_manager, args=(conn,addr)).start()







