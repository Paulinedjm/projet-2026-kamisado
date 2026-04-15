import socket 
import json

serverAddress= ("172.20.10.3", 3000)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((serverAddress))
    message= client.send()
    with open("eval.json", "w", encoding='utf-8') as 
    json.dump(fichier, indent=4, ensure_ascii=False)
    #Cette fonction prend un objet Python et le convertit en une chaîne de caractères formatée en JSON, 
    # sans l’écrire dans un fichier.
    
    client.send()
    response = client.recv(4).decode()
    print(response)