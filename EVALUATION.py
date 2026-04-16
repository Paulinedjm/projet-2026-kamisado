import socket 
import struct 
import json

serverAddress= ("172.20.10.3", 3000)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((serverAddress))
    


def envoyé(client):
    envoi= {
      "request": "subscribe",
      "port": 8888,
      "name": "fun_name_for_the_client",
      "matricules": ["12345", "67890"]
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

       
#execution

taille_envoyé, taille_attendu = envoyé(client) #recupérer la taille du messages envoyé

recevoir(client, taille_envoyé, taille_attendu)



"""
 if envoyé(client.send)== len(envoyé(envoi)):
        reçu={
          "response": "ok"
        }
        #transformer le message binaire en texte -> pour ensuite le transofrmer en dico
        response= json.loads(reçu.decode("utf-8"))
        #ouverture de fichier et mettre response en texte str sur le eval.json
        with open("eval.json", "w") as f : 
            json.dumps(response, indent=4)
"""