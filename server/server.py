#Library imports
import time
import socket
import threading
import cryptography
import os
import base64
import Cryptor
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto import Random
from Crypto.Cipher import PKCS1_v1_5
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


class Server:
    #init module will check if keys exist in program directory
    def __init__(self):
        if not os.path.exists('keys'):
            os.makedirs('keys')
        if not os.path.isfile('keys/private.pem'):
            self.keysetup()
        #if the keys are present the server will begin
        self.start_server()
        
    #module for keysetup, this takes place at the start if no keys are found  
    def keysetup(self):
        private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
            )
        #writes generated key to file
        with open('keys/private.pem', 'wb') as f:
            f.write(pem)
            
        public_key = private_key.public_key()
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        
        #writes public key to file
        with open('keys/public.pem', 'wb') as f:
            f.write(pem)
            

            
    #module to begin server code
    def start_server(self):
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        
        #assigning this staticly later
        host = input('Please enter a hostname or IP')
        port = int(input('Enter port to run the server on --> '))
        
        #tables for storing clients and their public keys
        self.clients = []
        self.pk = []
        
        #bind code
        self.s.bind((host,port))
        self.s.listen(100)
    
        print('Running on host: '+str(host))
        print('Running on port: '+str(port))

        self.username_lookup = {}
        self.key_lookup = {}


        #server loop code 
        while True:
            #accept connections
            c, addr = self.s.accept()
            
            #recieve username string
            username = c.recv(1024).decode() 
            print('New connection. Username: '+str(username))
            self.broadcast('New person joined the room. Username: '+username)
            
            #append username to the tables
            self.username_lookup[c] = username
            self.clients.append(c)
            
            #recieve user public key
            pk = c.recv(1024).decode()
            
            
            #append keys to tables
            self.key_lookup[c] = pk
            self.pk.append(pk)
            
             #Server pub key send
            key = open('keys/public.pem')
            server_pub = key.read()
            c.send(server_pub.encode())
            time.sleep(5)
            
            
            #threading code?
            threading.Thread(target=self.handle_client,args=(c,addr,)).start()
            
            
            
            
            

    def broadcast(self,msg):
        for connection in self.clients:
            connection.send(msg.encode())

    def handle_client(self,c,addr):
        while True:
            try:
                msg = c.recv(1024)
                msgdecode = msg.decode()
            except:
                c.shutdown(socket.SHUT_RDWR)
                self.clients.remove(c)
                
                print(str(self.username_lookup[c])+' left the room.')
                self.broadcast(str(self.username_lookup[c])+' has left the room.')

                break

            if msgdecode != '':
                print('New message: '+str(msgdecode))
                #enable this code to send encrypted messages to clients
                #for connection in self.clients:
                 #   if connection != c:
                  #      connection.send(msg)
                        
                if msgdecode.endswith('=='): 
                    decrypted = Cryptor.decrypt(msg.decode())
                    print('Decrypted message: ', decrypted)
                    for connection,key in zip(self.clients,self.pk):
                        if connection != c:
                           
                            #new code
                            connection.send(Cryptor.encrypt(decrypted, key))
                            #connection.send(decrypted.encode())
                        
         
            
                        
            

server = Server()
