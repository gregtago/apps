# apps

Les applications de l'Office Notarial, en pages HTML autonomes.

Chaque fichier `*.dc.html` est une application complète : tout (code, styles,
polices, ressources) est embarqué dans le fichier. Aucune installation, aucun
serveur, aucune dépendance — il suffit d'ouvrir le fichier dans un navigateur.
Les données restent sur le poste.

## Contenu

| Fichier | Application | Objet |
| --- | --- | --- |
| `index.html` | Accueil | La page qui présente et ouvre les sept outils |
| `alix.dc.html` | Alix — `alix.tagot.fr` | Les successions et les demandes aux organismes : le registre des courriers et des attentes |
| `henri.dc.html` | Henri — `henri.tagot.fr` | Les dossiers et les tâches : les petites choses à faire avant l'acte, en colonnes |
| `pierre.dc.html` | Pierre — `pierre.tagot.fr` | Les renseignements sur un immeuble à partir d'une adresse ou de ses parcelles, et les pièces officielles à annexer aux actes |
| `simone.dc.html` | Simone — `simone.tagot.fr` | Le lecteur PDF du rédacteur : on surligne ce qui compte dans l'acte, on récupère le texte |
| `scribe.dc.html` | Scribe | L'océrisation des pièces : rendre chaque scan recherchable, l'original intact |
| `lcbft.dc.html` | Portail LCB-FT | La vigilance : les parties passées au crible, la preuve conservée. Réservé à l'Office, la page ne donne pas d'accès |
| `portail-client.dc.html` | Portail client — `form.tagot.notaires.fr` | Le questionnaire en ligne du client, l'échange des RIB et l'origine des fonds |

## Poids des pages

Les images embarquées sont en WebP : 3,9 Mo pour l'ensemble des huit pages. Le script `outils/alleger-images.py`
fait cette conversion — à relancer après chaque nouvel export des pages :

```
python3 outils/alleger-images.py index.html *.dc.html
```

Il ne touche qu'aux images du manifeste (PNG → WebP, sans perte quand c'est
raisonnable) et laisse le reste de la page intact. Les quelques images
livrées très au-dessus de leur taille d'affichage sont redimensionnées ; la
liste est en tête du script, à revoir après un ré-export, car les
identifiants d'images changent à chaque fois.

## Utilisation

Ouvrir `index.html` dans un navigateur, ou ouvrir directement le fichier d'une
application. Les liens de la page d'accueil pointent vers les fichiers voisins,
donc les huit fichiers doivent rester dans le même répertoire.

Les pages des deux portails sont volontairement courtes et ne contiennent
aucune image : elles ont été composées à partir de la fiche de Pierre (mêmes
polices, même gabarit), sans passer par un export.

Le dépôt peut aussi être publié tel quel comme site statique : `index.html` en
racine sert de page d'accueil.
