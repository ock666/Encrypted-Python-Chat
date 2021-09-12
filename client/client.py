import socket
import os
import threading
import cryptography
import base64
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from binascii import hexlify
from Crypto.Hash import SHA
from Crypto import Random
from Crypto.Cipher import PKCS1_v1_5
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding




class Client:

    #init module will check if keys exist in program directory
    def __init__(self):
        if not os.path.exists('keys'):
            os.makedirs('keys')
        if not os.path.isfile('keys/private.pem'):
            self.keysetup()
        #if the keys are present the client will begin
        self.create_connection()
        
        
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
        
        #writes generated key to file
        with open('keys/public.pem', 'wb') as f:
            f.write(pem)
            
    

    def create_connection(self):
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        
        while 1:
            try:
                host = input('Enter host name --> ')
                port = int(input('Enter port --> '))
            
                self.s.connect((host,port))
                
                break
            except:
                print("Couldn't connect to server")
        
        #input username and send to server
        self.username = input('Enter username --> ')
        self.s.send(self.username.encode())
        
        #open public key file and send to server
        pk = open('keys/public.pem')
        public = pk.read()
        self.s.send(public.encode())
        
        
        #recieve server public key
        server_pub = self.s.recv(2048)
        
        #write server public key to file
        with open('keys/serverkey.pem', 'wb') as f:
            f.write(server_pub)
        


        
        message_handler = threading.Thread(target=self.handle_messages,args=())
        message_handler.start()

        input_handler = threading.Thread(target=self.input_handler,args=())
        input_handler.start()
    
    def encrypt(message):
    
        with open('keys/serverkey.pem', 'rb') as k:
            key = RSA.importKey(k.read())
        
        cipher = PKCS1_v1_5.new(key)
        byte_array = cipher.encrypt(message.encode())
        return base64.b64encode(byte_array)

    def decryptor(encrypted):
        b64decode = base64.b64decode(encrypted)
        with open("keys/private.pem", "rb") as k:
            key = RSA.importKey(k.read())

        decipher = PKCS1_v1_5.new(key)
        return decipher.decrypt(b64decode, None).decode()
 
    
    
    
        

    def handle_messages(self):
        
        while 1:
            msg = self.s.recv(2048)
            msgdecode = msg.decode()
            if msgdecode.endswith('=='):
                print('New Message: ',Client.decryptor(msgdecode))
            else:
                print(msgdecode)
                
            #print(self.s.recv(2048).decode())
    
    #module for handling messages and clientside input
    def input_handler(self):
        
        while 1:
            precode = (self.username+' - '+input())
            message = Client.encrypt(precode)
            self.s.send(message)

client = Client()
