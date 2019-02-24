import socket 
import ProtocolTranslator
from PeerList import PeerList



def Main(): 
	# local host for testing
    host = '127.0.0.1'

	# port for connecting to the Registration Server
    port = 65243


    # This client's cookie
    cookie = -1
    
    # Peer List for this client
    peer_list = None
    
    while True:
    
        cmd = input("Enter Command: ")
        print()
        
        #TODO: Currently an issue with a user registering twice
        if cmd == "Register":

            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
            s.connect((host,port))
            
            request = ProtocolTranslator.registerQueryToProtocol( host, 11000, cookie )
        
            print(request)
        
            s.send(request.encode('ascii')) 

            response_bytes = s.recv(2048) 

            response = str(response_bytes.decode('ascii'))
     
            print(response) 
        
            cookie = ProtocolTranslator.registerResponseToElements( response )
        
            s.close()
            
        elif cmd == "PQuery":
            
            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
            s.connect((host,port))
            
            request = ProtocolTranslator.pqueryQueryToProtocol( cookie )
        
            print(request)
        
            s.send(request.encode('ascii')) 
            response = ''
            while True:
                response_bytes = s.recv(2048) 

                response += str(response_bytes.decode('ascii'))
                
                if response[-4] = "END\n":
                    break
        
            print(response)
     
            success, p_list = ProtocolTranslator.pqueryResponseToElements( response )
            
            if success:
                peer_list = p_list

            s.close()
        
        elif cmd == "Leave":
        
            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
            s.connect((host,port))
            
            request = ProtocolTranslator.leaveQueryToProtocol( cookie )
        
            print(request)
        
            s.send(request.encode('ascii')) 
            
            response_bytes = s.recv(2048) 

            response = str(response_bytes.decode('ascii'))
     
            print(response) 
        
            status = ProtocolTranslator.leaveResponseToElements( response )
            
            if status == True:
                cookie = -1
            
            s.close()

        elif cmd == "KeepAlive":
            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
            s.connect((host,port))
            
            request = ProtocolTranslator.keepAliveQueryToProtocol( cookie )
        
            print(request)
        
            s.send(request.encode('ascii')) 
            
            response_bytes = s.recv(2048) 

            response = str(response_bytes.decode('ascii'))
     
            print(response) 
        
            status = ProtocolTranslator.keepAliveResponseToElements( response )
            
            s.close()
            
        
        elif cmd == "Exit":
            break
        else:
            print("Invalid Command")

if __name__ == '__main__': 
	Main() 
