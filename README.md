# GodBot

GodBot est un bot discord implémentant 2 fonctionnalitées:
  - un mini jeu de guerre stratégique textuel
  - une configuration simple du bot via commande utilisateur

Installation:
- Installer python 3.9
- Télécharger la dernière release sur https://github.com/Shirakawa42/GodBot/releases
- Dezipper le fichier téléchargé
- lancer la commande "python3 -m pip install GodBot-0.0.2.tar.gz" dans le dossier dezippé
- Créer la variable d'environnement "DISCORD_TOKEN" contenant votre token de bot discord

Utilisation d'une base de donnée (optionnel, nécessite une base de donnée postgreSQL, permet de sauvegarder les joueurs et les configurations):
- Créer une base de donnée appelée "godbot"
- Créer la table "players" avec les champs: "name" varchar(255), "race" varchar(255), "level" int, "tech" int, "money", int
- Créer la table "ships" avec les champs: "name" varchar(255), "aoe" int, "max_hp" int, "damages" int, "level" int, "tech" int, "player_name" varchar(255)
- Créer la table "whens" avec les champs: "subjects" varchar(255), "comparators" varchar(255), "cmp_param" varchar(255), "actions" varchar(255), "action_param" varchar(255)
- Créer les variables d'environnement "RDS_DB_HOST" et "RDS_DB_PWD" contenant le lien vers votre base de donnée et son mot de passe

Lancement du bot:
```
from GodBot.god_bot import GodBot
bot = GodBot()
bot.start_bot()
```

Une fois lancé, la commande !help sur votre serveur discord vous donnera un aperçu des possibilités.

```
HandleMessage:
  reset      !reset: Delete every rules made with !when command
  when       !when subject comparator text action text: Create a rule
  whens      Show all !when
RpgCommands:
  attack     !attack other_player: Fight against another player
  buildShip  !buildShip name nb_targets tankiness investment: Use money to bu...
  initPlayer !initPlayer "race": Initialize yourself
  players    List all players
  save       Save the game, an auto save is done every 5 minutes
  send       Send money or ship to another player
  showMe     !showMe: Show all informations about yourself
​No Category:
  help       Shows this message

Type !help command for more info on a command.
You can also type !help category for more info on a category.
```
