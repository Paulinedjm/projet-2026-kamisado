import socket 
import json

serverAddress= ("172.20.10.3", 3000)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((serverAddress))
    

def recevoir(client):
    reçu={
      "response": "ok"
    }
    message_reçu_erreur= 
    {
      "response": "error",
      "error": "error message"
    }
    
    with open("eval.json", "w") as message_reçu : 
        message_reçu= json.loads(message_reçu)
        message= client.recv(4).decode()
    print(message)
   
    

def envoyé(client):
    envoyé= {
      "request": "subscribe",
      "port": 8888,
      "name": "fun_name_for_the_client",
      "matricules": ["12345", "67890"]
    }
    
    message_envoyé= json.dumps(envoyé)

    client.send(message_envoyé.encode())



#requête serveur 

request_envoyé=
{
  "request": "ping"
}

request_reçu= 
{
  "response": "pong"
}



