import socket 
import struct 
import json


def envoyé(client):
    envoi= {
      "request": "subscribe",
      "port": 8888,
      "name": "Pauline et Cindy",
      "matricules": ["24343", "24160"]
    }
    #preparation du message + taille
    message_json= json.dumps(envoi).encode("utf-8")
    taille= len(message_json)

    #envoie (4 octect, taille, contenu du message)
    header=struct.pack( "I", taille)

    taille_totale=client.send(header+ message_json)
    
    return taille_totale, len(header)+len(message_json)


def recevoir(client, taille_envoyé, taille_attendu):

    if taille_envoyé== taille_attendu :
        
    
        # lire la taille de la réponse 4 oct
        response= client.recv(4)
        taille_response= struct.unpack("I", response)[0]
    
        #recevoir 
        data= client.recv(taille_response)
        # 3. On décode et on transforme en dictionnaire
        response = json.loads(data.decode("utf-8"))
        
        # 4. Écriture dans le fichier
        with open("eval.json", "w") as f:
            json.dump(response, f, indent=4)
   
    else : 
        message_reçu_erreur= {
          "response": "error",
          "error": "error message"
        }
        with open("eval.json", "w") as f:
            json.dump(message_reçu_erreur, f, indent=4)


def attendre_ping():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(('', 8888))
        listener.listen(1)
        print("En attente de pings...")

        while True:
            server_sock, addr = listener.accept()
            with server_sock:
                # 1. On lit d'abord les 4 octets du header
                header = server_sock.recv(4)
                # 2. On calcule la taille du message
                taille = struct.unpack("I", header)[0]
                # 3. On lit exactement le nombre d'octets annoncés
                data = server_sock.recv(taille)
                # 4. MAINTENANT on peut faire le json.loads
                requete = json.loads(data.decode("utf-8"))

                if requete.get("request") == "ping":
                    # Pour répondre, on fait l'inverse :
                    reponse_dict = {"response": "pong"}
                    reponse_json = json.dumps(reponse_dict).encode("utf-8")
                    header_resp = struct.pack("I", len(reponse_json))
                    
                    server_sock.sendall(header_resp + reponse_json)
                    print(f"Ping reçu de {addr} -> Pong envoyé !")

serverAddress= ("172.17.10.46", 3000)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((serverAddress))  
    #execution

    taille_envoyé, taille_attendu = envoyé(client) #recupérer la taille du messages envoyé
    
    recevoir(client, taille_envoyé, taille_attendu)
    attendre_ping()
