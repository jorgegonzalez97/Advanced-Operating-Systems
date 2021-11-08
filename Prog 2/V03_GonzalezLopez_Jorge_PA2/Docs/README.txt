There are two python scripts:

	- server.py: It makes the indexing server start running

	- client.py: It makes one peer node (client + server) start running






To run the server the following command is needed:

	python3 server.py <IP_ADDRESS> <PORT>
	
	

<IP_ADDRESS>: IP address of the server (e.g. 127.0.0.1)

<PORT>: Server port (e.g. 3000)
		
		
			

Once the server is running it will show the following message: 

	Listening as <IP_ADDRESS> : <PORT>

Then, every time a client connects to the server, it will be printed and saved in the log.log file (in the folder Out).






To run the client the following command is needed:

	python3 client.py <IP_ADDRESS> <IND_SERVER_PORT> <OWN_SERVER_PORT> <FOLDER_NAME>
	
	

<IP_ADDRESS>: IP address of the server (e.g. 127.0.0.1)

<IND_SERVER_PORT>: Indexing server port (e.g. 3000)

<OWN_SERVER_PORT>: Owns server port (e.g. 5000)

<FOLDER_NAME>: Name of the folder where the CLIENT stores its files (e.g. client_files) 
		IMPORTANT NOTE: The folder must exist




Once the client is running it will show the following message: 

	Connected to INDEXING SERVER: <IP_ADDRESS> : <IND_SERVER_PORT>
	
	Listening as <IP_ADDRESS> : <OWN_SERVER_PORT>
	

Then, the client waits until a command is written:

	-register: The client gets register for P2P downloads (the indexing server gets the clients server port and the list of files it hosts). 

	- unregister: The client unregisters for P2P downloads at the indexing server.

	- delete <FILE>: It will delete <FILE> from its own folder (if exists) and update its list of files that the indixing server has.
	
	-get_files_list: The client receives a list of the files that all the peer nodes that are registered host.

	- download <FILE>: The client receives a list of peers that host the <FILE> requested, chooses one of them randomly, establishes a connection with it, downloads the file and uploads the list of files it hosts (only if the client is registered).
	
All other commands will return: Command is not supported.
