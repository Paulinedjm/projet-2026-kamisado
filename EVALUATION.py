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
        #On décode et on transforme en dictionnaire
        response = json.loads(data.decode("utf-8"))
        
        # Écriture dans le fichier
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
    # On crée un nouveau socket pour écouter le serveur
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        # Permet de relancer le script sans attendre que le port se libère
        #listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(('', 8888))
        listener.listen(1)
        print("En attente de pings du serveur sur le port 8888...")

        while True:
            # On accepte la connexion entrante du serveur
            server_sock, addr = listener.accept()
            with server_sock:
                # Lecture du ping (taille + contenu)
                header = server_sock.recv(4)
                if header:
                    taille = struct.unpack("I", header)[0]
                    data = server_sock.recv(taille)
                    requete = json.loads(data.decode("utf-8"))

                    if requete.get("request") == "ping":
                        # Préparation et envoi du pong
                        reponse = json.dumps({"response": "pong"}).encode("utf-8")
                        taille_resp = struct.pack("I", len(reponse))
                        server_sock.sendall(taille_resp + reponse)
                        print(f"Ping reçu de {addr} -> Pong envoyé !")

serverAddress= ("172.17.10.50", 3000)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((serverAddress))  
    taille_envoyé, taille_attendu = envoyé(client) #recupérer la taille du messages envoyé
    
    recevoir(client, taille_envoyé, taille_attendu)

attendre_ping()


