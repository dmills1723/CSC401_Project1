'''
    file:   RFCServer.py
    author: Daniel Mills (demills)
    Implementation of a multithreaded server that provides two services.
       1) RFCQuery : A peer requests this peer's current RFC index.
       2) GetRFC   : A peer requests to download a specific RFC document from this peer.
    The RFCServer should be instantiated by the RFCClient before a peer registers
    with the RegistrationServer.
'''

import socket
import threading
import time
import signal, os
import ProtocolTranslator

'''
    Class for threads spawned by the server to handle communication with
    another peer.
'''


class PeerThread(threading.Thread):
    def __init__(self, ip_addr, port, socket, rfc_index):
        threading.Thread.__init__(self)
        self.ip_addr = ip_addr
        self.port = port
        self.socket = socket
        self.rfc_index = rfc_index

    def hasLocalRFC(self, rfc_num):
        rfc_path = os.path.join(os.path.curdir, "RFCs", "rfc%s.txt" % rfc_num)
        print(rfc_path)
        return os.path.isfile(rfc_path)

    def run(self):
        request_bytes = self.socket.recv(1024)

        # convert the request in bytes to string
        request = str(request_bytes.decode('ascii'))

        print(request)

        # obtains the method of this protocol
        method = request.splitlines()[0]

        if method == "RFCQuery":
            nonEmptyIndex = (self.rfc_index.size() > 0)

            # sends back a response message with the cookie
            response = ProtocolTranslator.rfcQueryResponseToProtocol(nonEmptyIndex, "FAKE INDEX. TODO")

            # response = ProtocolTranslator.rfcQueryResponseToProtocol( nonEmptyIndex, str( self.rfc_index ))
        elif method == "GetRFC":
            rfc_num = ProtocolTranslator.getRfcQueryToElements(request)

            # Checks if local file for RFC exists. Passes this to ProtocolTranslator below.
            print(rfc_num)
            has_file = self.hasLocalRFC(rfc_num)
            print("has file: %s\n" % has_file)

            response = ProtocolTranslator.rfcQueryResponseToProtocol(has_file, "")

        else:
            response = ProtocolTranslator.genericBadRequestResponseToProtocol()

        print(response)

        # translates the response protocol into bytes
        response_bytes = response.encode('ascii')

        # sends the response to the peer client
        self.socket.send(response_bytes)


'''
'''


class RFCServer():
    '''
        Initializes the RFCServer:
            - Creates and binds a socket to listen for incoming peers.
            - Sends the client the port chosen to listen on.
            - Instantiates instance variables:
                rfc_index: Initial RFCIndex passed from ClientPeer.
                serv_sock: Socket the server listens for peers on.
                serv_pipe: Pipe for communication with ClientPeer.
                serv_port: Port number the server is listening on.
        Then, starts the main server function "runServer()". The server will
        remain in this function until PeerClient sends a SIGTERM from PeerClient.

    '''

    def __init__(self, serv_pipe, rfc_index):
        # Initializes the RFC index.
        self.rfc_index = rfc_index

        # Creates socket to listen for incoming peers on.
        self.serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Gets this computer's IP address which the socket will listen on.
        ip_addr = self.getIPAddress()

        # Binds socket to a random, available port.
        self.serv_sock.bind((ip_addr, 0))

        # Gets the port number "serv_sock" is bound to ...
        self.serv_port = self.serv_sock.getsockname()[1]

        # ... and sends it back to the Client.
        self.serv_pipe = serv_pipe
        self.serv_pipe.send(self.serv_port)

        print("RFCServer: %s\n" % os.getpid())

    '''
        Returns this computer's IP address. 
    '''

    def getIPAddress(self):
        # Creates socket to Google's nameserver.
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))

        # Gets this computer's IP address from the socket connection.
        ip_addr = sock.getsockname()[0]

        sock.close()
        return ip_addr

    def cleanup(self, worker_threads):
        self.serv_sock.close()
        for thread in worker_threads:
            thread.join()
        print("finished cleanup. exiting....")

    def run(self):
        worker_threads = []
        print(self.serv_port)

        while True:
            try:
                self.serv_sock.listen()
                (client_sock, (ip_addr, port)) = self.serv_sock.accept()

                # Check if an updated RFC index has been sent from the client.
                # Update the RFC index if so.
                if (self.serv_pipe.poll()):
                    self.rfc_index = self.serv_pipe.recv()

                peer_thread = PeerThread(ip_addr, port, client_sock, self.rfc_index)
                peer_thread.start()

                worker_threads.append(peer_thread)

            except KeyboardInterrupt:
                self.cleanup(worker_threads)
                break