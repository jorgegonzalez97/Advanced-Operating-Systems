There are two python scripts:

	- super_peer.py: It deploys a super peer node

	- weak_peer.py: It deploy a weak peer node





To run a super peer node the following command is needed:

	python3 super_peer.py <IP_ADDRESS> <OWN PORT> <NEIGHBORS SUPER PEER PORTS>
	
	

<IP_ADDRESS>: IP address of the server (e.g. 127.0.0.1)

<OWN PORT>: Server port (e.g. 3000)

<NEIGHBORS SUPER PEER PORTS>: All ports of neighbors super peers separated by blank spaces (e.g. 3001 3002 3003 3004)
		
Once the super node is running it will wait until all the neighbours indicated in the arguments are correctly connected between them, showing the following message: 

	Listening as <IP_ADDRESS> : <PORT>

and a set number of clients connected (super peers).


Then, every time a weak node connects to the server, it will connect to the super node and automatically register for P2P downloads.





To run the weak peer nodes the following command is needed:

	python3 week_peer.py <IP_ADDRESS> <SUPER_PEER_PORT> <SUPER_PEER_TOPOLOGY> <SERVER_PORT> <FOLDER_NAME>
	
	

<IP_ADDRESS>: IP address to connect to the super node (e.g. 127.0.0.1)

<SUPER_PEER_PORT>: Super peer server port (e.g. 3000)

<SUPER_PEER_TOPOLOGY>: 'all' or 'linear' ( all-to-all sets up a TTL of 1 for the queries and 'linear' a TTL of the total number of super peers minus one) 

	NOTE: 	if the topology is 'all' -> the super_peers must be deployed with all the other super_peers ports as arguments (they are all neighbors).
		if the topology is 'linear' -> each super peer has to be deployed either with just one or two super_peer neighbors port (just their direct neighbors).

<OWN_SERVER_PORT>: Owns server port (e.g. 6000)

<FOLDER_NAME>: Name of the folder where the weak node stores its files (e.g. client_files) 
		IMPORTANT NOTE: The folder must exist






Once the weak node is running it will show the following message: 

	Connected to SUPER PEER: <IP_ADDRESS> : <ISUPER_PEER_PORT>
	
	Listening as <IP_ADDRESS> : <OWN_SERVER_PORT>
	
	Registered for Peer-to-Peer downloads
	
	
	

Then, the client waits until a command is written:

	- unregister: The weak peer unregisters for P2P downloads at the super peer node that it is connected to.

	-register: The weak peer gets register again for P2P downloads. 

	- delete <FILE>: It will delete <FILE> from its own folder (if exists) and update its list of files that the super peer node has.
	
	-get_files_list: The weak peer node receives a list of the files that all the weak peer nodes that are registered in THE SAME SUPER NODE host.

	- query <FILE>: The weak peer sends a download request of <FILE>. Then, the weak peer can keep typing and sending more commands, but keeps listening for a queryhit to download the file as soon as it receives it.
	
All other commands will return: Command is not supported.




















