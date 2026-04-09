import socket
import json

serverAddress = ("127.17.10.41", 3000)

def send_json(sock, data):
    message = json.dumps(data).encode("utf-8")
    sock.sendall(message)

def receive_json(sock):
    message = sock.recv(4).decode('utf-8')
    return json.loads(message)

data = {
  "request": "subscribe",
  "port": 3000,
  "name": "fun_name_for_the_client",
  "matricules": ["24343", "24160"] }


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client: 
    client.connect(serverAddress)
    send_json(client, data)
    
    response = receive_json(client)
    