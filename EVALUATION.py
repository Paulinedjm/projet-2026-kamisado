import socket 
import json

serverAddress= ("127.17.10.41", 3000)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect(serverAddress)
    message= client.send()
    with open("eval.json", "w")
    client.send()
    response = client.recv(4).decode()
    print(response)