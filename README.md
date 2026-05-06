# projet-2026-kamisado

## Introduction : Negamax et Alpha-beta Pruning

Notre agent repose sur l'algorithme Negamax et Alpha-beta Pruning, pour la prise de décision. Ce procédé nous permet d'évaluer la qualité des positions respectives de chaque joueur afin de déterminer l'état du plateau. En partant du principe que l'adversaire adopte systématiquement une stratégie rationnelle et optimale, l'algorithme anticipe ses réponses pour identifier le coup le plus avantageux. Cette approche permet à l'agent de maximiser ses propres gains tout en minimisant les opportunités de l'opposant.

L'objectif de notre heuristique est de quantifier d’un plateau de jeu sur une échelle allant de -1 à 1.Pour cela, notre algorithme s’appuie sur une hiérarchie de critères tactiques sur les conditions de victoire imédiate, le deadlock et la mobilité des tours.

## Stratégies

En premier, on analyse si l'état actuelle peut mener a une victoire immédiate. Si l'état actuel du jeu permet à l'une de nos tours d'atteindre la ligne d'arrivée, nous attribuons un score maximal de +1. À l'inverse, si la situation permet à l'adversaire de gagner au coup suivant, le score tombe à -1.

Ensuite, on vérifie si un joueur se retrouve sans aucun mouvement possible avec la tour imposée, ce qui serrait un handicape majeur. Si un joueur se retrouve dans cette impasse, nous appliquons une lourde pénalité de -4.

L'heuristique parcourt ensuite l'ensemble du plateau pour évaluer le potentiel de chaque tour présente. L'algorithme vérifie pour chaque tour, si elle possède un mouvement légal capable d'atteindre la ligne de but adverse. Si c'est l'une des nôtres, on ajoute +1.5. Si c'est une tour adverse, on retire 2 points. On retire plus de points pour une menace ennemie qu’on en gagne pour une attaque, car il est plus important d'interrompe le progression de l'adversaire afin de provoquer un blocage(Deadlock).
Ensuite, le code calcule le nombre total de coups possibles pour nous (my_mobility) et pour l'adversaire (opps_mobility). On rajoute (my_mobility - opps_mobility) \* 0.1 a notre score. Cela aide l'IA à choisir des positions où elle a de l'espace et du choix.

Pour finir, on utilise la fonction "tanh" sur le score total. Cela sert à normaliser le résultat pour qu'il reste entre -1 et 1, peu importe si les points accumulés sont très élevés. Cela permet d'avoir une note facile à comparer pour l'IA.

## Les matricules

(Cindy Njeumi Guetcho et Pauline de Jambiline) : 24343 - 24160

## Les bibliothèques utilisés :

- "socket" : nous permet de communiquer avec un serveur
- "struct" : nous permet d'encoder et décoder des messages par leurs tailles
- "json" : nous permet de recevoir l'état de jeu et d'envoyer des messages au serveur
- "math" : nous permet de normaliser le score dans def evaluate (math.tanh)
