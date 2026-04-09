import socket
import json
import struct 

serverAddress = ("172.17.10.41", 3000)

def send_json(sock, data):
    message = json.dumps(data).encode("utf-8")
    length = struct.pack('I', len(message)) 
    sock.sendall(length)
    sock.sendall(message)


def receive_json(sock):
   length_data = sock.recv(4)
   if not length_data:
        return None
   length = struct.unpack('I', length_data)[0]

   message = sock.recv(length).decode('utf-8')
   return json.loads(message)

data = {
  "request": "subscribe",
  "port": 8888,
  "name": "Pauline",
  "matricules": ["24343", "24160"] }


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client: 
    client.connect(serverAddress)
    send_json(client, data)
    
    response = receive_json(client)


    