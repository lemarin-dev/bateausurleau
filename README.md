# Bateau autonome Virtual Regatta

Le projet est en Python 3.6 et il faut installer avec Pip les modules suivants: requests, websocket
On peut les installer avec la commande: pip3 install -r requirements.txt

Avant de démarrer le programme, il faut mettre les valeurs suivantes:

Adresse mail connecté à Virtual Regatta

Mot de passe de Virtual Regatta

Et clé API de MyBoatVRO, contactez moi par email pour en obtenir une (martinmoor43@gmail.com). Cela peut prendre un peu de temps.

MyBoatVRO:
Pour demander un compte, envoyez un email avec un nom ou un pseudo, une adresse email, et la raison de votre demande.
Pour vérifier si votre compte marche, https://myboatvro.000webhostapp.com/info.php?apikey= <-- Votre clé API
Cette page permet de voir vos crédits restants, le nombre d'utilisations, et le status du compte.
Attention les comptes ont une limite, ne partagez votre compte MyBoatVRO.

Le script Python:
Il y a une commande incluse, mais d'autres peuvent être ajoutées.
Il faut les écrire dans la forme suivante: 
user={"@class":".AccountDetailsRequest","requestId":"63744542013080000_"+str(requestid())}\n
requestdata(user)

Pour trouver des nouvelles commandes, il suffit d'intercepter le traffic de l'application Virtual Regatta
 
 Bonne chance !!
