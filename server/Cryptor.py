from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64

def encrypt(message, key):
    pubkey = RSA.importKey(key)    
    cipher = PKCS1_v1_5.new(pubkey)
    byte_array = cipher.encrypt(message.encode())
    return base64.b64encode(byte_array)

def decrypt(encrypted):
    b64decode = base64.b64decode(encrypted)
    with open("keys/private.pem", "rb") as k:
        key = RSA.importKey(k.read())

    decipher = PKCS1_v1_5.new(key)
    return decipher.decrypt(b64decode, None).decode()
 
    
    


