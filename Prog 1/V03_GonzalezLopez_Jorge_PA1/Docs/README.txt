There are two python scripts:

	- server.py: It makes the server start running

	- client.py: It makes one client start running
	  (can be executed several times to have multiple clients)






To run the server the following command is needed:

	python3 server.py <IP_ADDRESS> <PORT> <FOLDER_NAME>
	
	

<IP_ADDRESS>: IP address of the server (e.g. 127.0.0.1)

<PORT>: Server port (e.g. 3000)

<FOLDER_NAME>: Name of the folder where the SERVER hosts the files (e.g. files) 
		IMPORTANT NOTE: The folder must exist
		
		
			

Once the server is running it will show the following message: 

	Listening as <IP_ADDRESS> : <PORT>

Then, every time a client connects to the server, it will be printed and saved in the log.log file (in the folder Out).






To run the client the following command is needed:

	python3 client.py <IP_ADDRESS> <PORT> <FOLDER_NAME>
	
	

<IP_ADDRESS>: IP address of the server (e.g. 127.0.0.1)

<PORT>: Server port (e.g. 3000)

<FOLDER_NAME>: Name of the folder where the CLIENT stores its files (e.g. client_files) 
		IMPORTANT NOTE: The folder must exist




Once the client is running it will show the following message: 

	Connected to: <IP_ADDRESS> : <PORT>

Then, the client waits until a command is written:

	- get_files_list: It will return all the files that the server has in its folder.

	- delete <FILE>: It will delete <FILE> from the server folder (if exists).

	- modify <FILE> <NEW_NAME>: It will modify the name of <FILE> (if exists) for <NEW_NAME>.

	- add <FILE>: It will add clients <FILE> (if exists) into server files.
	
	-close: The connection is terminated and the execution of the client stops.

	- download <MODE> <FILES>:

		- <MODE>: Can be either serial (download one file after another) or parallel (several connections for concurrent downloads).

		- <FILES>: the name of files from the server that want to be download separated by blank spaces. If a file does not exist, the server will notify the client but continue with the rests of the files.






The other way to make the server and the clients work is to run the .sh scripts. To do so:

Server:
	- Edit bash script with the IP address, Port and Folder.
	- Open a terminal and go to the directory of server.py.
	- Run the command:  ./s.sh

Client:
	- Edit bash script with the IP address, Port and Folder.
	- Open a terminal and go to the directory of client.py.
	-There are three different bash scripts:
	
		- ./q2.sh : Generates 4 concurrent clients that download 3 files at the same time. (Files must be edited inside the bash script)
		- ./q3.sh <N_clients> : Generates N concurrent clients that download 10 files in parallel (10 threads each client) (Files must be edited inside the bash script)
		- ./q4.sh <File> : Generates 4 concurrent clients that download <File> 10 times in parallel (10 threads each client)




