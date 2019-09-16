# CSC401_Project1 #

## Project 1 for CSC401 ##

We used Python to code a representation of a simple peer-to-peer (P2P) system with a distributed index (DI) in order to transfer RFC (Request For Comments) files within a community of peers.

The composition of parts within our P2P/DI system include:
* Registration Server (RS)
  * Peer List
* Application Layer Protocol (P2P)
  * Peer-to-Peer Communication
  * Peer-to-RS Communication
* Peers
  * RFC Index
    * RFC Number
    * RFC Title
    * Peer Hostname
  * RFC Server
  * RFC Client


_A general example of message flows within our system (from project guidelines pdf):_

Before it joins the system, A first instantiates an RFC server process listening to any available local port.
In Step 1, Peer A registers with the RS, provides the local port number for each RFC index, and receives a
cookie (if this is not the first time that Peer A registers with the RS, then it provides the cookie it received
earlier in its Register message). The RS updates A’s record to active and initializes the corresponding TTL
value; if this was the first time A registered, then the RS creates a new peer record for A and adds it to its
peer index. In Step 2, Peer A issues a PQuery message to the RS, and in response it receives a list of active
peers. Recall that the list of peers returned by the RS includes the port number used by each peer’s RFC
server. Let us assume that Peer B is in this active list, and that B has the RFC that A is looking for. In
Step 3, A issues an RFCQuery message to B, and in response it receives the RFC index that B maintains.
A merges B’s RFC Index with its own index. Since we have assumed that B has the desired RFC, A then
in Step 4 issues a GetRFC message to B and downloads the RFC text document. Finally, in Step 5, Peer A
sends a Leave message to the RS and leaves the system; the RS updates A’s record to inactive.

## Prerequisites ##

Install Python version 3.6 for this project

Run this program on an Ubuntu 16.04 system

Input this command into a terminal window to install the _numpy_ library:
```
sudo apt-get install python3-numpy
```

## Run Program ##

To locally run this program:

  1) In order to run the RS process, open a terminal window and input
```
python3 RegistrationServer.py
```
A hostname is printed on the next line --> 'Host: * * . * * * . * * . * * *'
Use it to connect future peers to the server

  2) Initialize a local set of RFC files within a directory labeled 'RFCs' (an empty directory with that name will automatically be created for every peer that is spawned)

  3) In order to add a single client (peer) to the system, open a terminal window input:
```
python3 ClientPeer.py '**.***.**.***'
```
  4) Repeat this step to add more peers to the community

To generate the cumulative download time profile for Task 1:
    0) Create 6 directories (or just 2 to see the process) and copy the project folder into each of these.

    1) In 5 of these, delete all the files in the "RFCs" directory.

    2) Start the RS process:

python3 RegistrationServer.py

    3a) In the project folder with nonempty "RFCs" directory:

python3 <local_ip_address> ClientPeer.py

    3b) Then:
"Register"

    4a) In the 5 folders with empty "RFCs" directories:
python3 <local_ip_address> ClientPeer.py <input.txt 2> times.txt

The files "times.txt" contain the Unix epoch time each RFC was downloaded and written locally. Note that running these in 'parallel' takes fast fingers. We had trouble starting 5 scripts in different directories simultaneously, both using python's "pexpect" library and BASH scripts, so it's a crude solution.
  
## Commands ##

The main menu for this program contains several options for client peers:

(1) Register, (2) PQuery (3) RFCQuery (4) DownloadRFC, (5) KeepAlive, (6) Leave, (7) Exit

User can enter commands in client terminal window

1) To register with the registration system (RS):
```
Register
```

2) To receive a list of all peers registered on the registration system (RS):
```
PQuery
```

3) To merge your local RFC Index with all peers who are registered and active on the registration system (RS):
```
RFCQuery
```

4) To download a specific RFC by calling PQuery (searching through the peer list to find a peer with the specific RFC) and calling RFCQuery (continuously merge RFC Index) in order to find the RFC document and transfer the file to your local directory 'RFCs':
```
DownloadRFC
```
The program will ask the user to enter the specific four-digit RFC number:
```
****
```

5) To tell the registration server (RS) to reset the TTL (time to live) in order to have the peer remain active:
```
KeepAlive
```

6) To leave the registration server (RS) and mark the peer as inactive:
```
Leave
```

7) To exit the program successfully:
```
Exit
```

**Note:** This program prints communication crumbs for each response message sent over the TCP socket connection for both peer-to-server and peer-to-peer communication. This is to show successful or failed TCP requests.

## Authors ##

* Daniel Mills
* Jonathan Balliet
* Anuraag Agarwal
