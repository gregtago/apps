#!/usr/bin/env python3
"""Allège les pages autonomes en ré-encodant les images qu'elles embarquent.

Les pages `*.dc.html` transportent leurs images dans un manifeste JSON, en
base64 (`<script type="__bundler/manifest">`). Le chargeur monte chaque
image en blob typé par le champ `mime` du manifeste : le navigateur choisit
son décodeur d'après ce champ, jamais d'après une extension de fichier. On
peut donc remplacer les octets PNG par du WebP sans toucher au reste de la
page — les uuid, le gabarit et la substitution uuid → blob sont inchangés.

Deux leviers :
  1. PNG → WebP, sans perte quand l'écart avec le mode avec perte reste
     raisonnable (les captures d'écran gardent leur texte au pixel près) ;
  2. redimensionnement des rares images livrées très au-dessus de leur
     taille d'affichage (voir REDIMENSIONNER).

Usage : python3 outils/alleger-images.py index.html *.dc.html
Dépendance : Pillow (pip install pillow).
"""
import base64
import io
import json
import re
import sys

from PIL import Image

# Préfixe d'uuid → largeur maximale, pour les images livrées bien au-dessus
# de la taille à laquelle la page les affiche. À revoir si les pages sont
# ré-exportées : les uuid changent à chaque export.
REDIMENSIONNER = {
    '2fad6056': 256,   # index.html    — illustration Scribe, affichée en 64 px
    'f9eeac91': 900,   # scribe.dc     — la même, affichée en 300 px
    '337096e3': 810,   # henri.dc      — capture iPhone, affichée en 270 px
}

# On garde le sans perte tant qu'il ne dépasse pas ce multiple du mode avec
# perte : le texte des captures reste net, sans payer trop cher.
TOLERANCE_SANS_PERTE = 1.6

MANIFESTE = re.compile(
    r'(<script type="__bundler/manifest">\s*)(\{.*?\})(\s*</script>)', re.S)


def encoder(image, **options):
    tampon = io.BytesIO()
    image.save(tampon, 'WEBP', method=6, **options)
    return tampon.getvalue()


def sans_alpha(image):
    """Retire une couche alpha entièrement opaque : plus léger, identique."""
    if image.mode == 'RGBA' and image.getchannel('A').getextrema() == (255, 255):
        return image.convert('RGB')
    return image


def alleger(png, uuid):
    image = Image.open(io.BytesIO(png))
    image.load()
    if image.mode == 'P':
        image = image.convert('RGBA')
    image = sans_alpha(image)

    largeur = REDIMENSIONNER.get(uuid[:8])
    if largeur and image.width > largeur:
        hauteur = round(image.height * largeur / image.width)
        image = image.resize((largeur, hauteur), Image.LANCZOS)
        return encoder(image, quality=90), 'redimensionné + q90'

    sans_perte = encoder(image, lossless=True)
    avec_perte = encoder(image, quality=90)
    if len(sans_perte) <= TOLERANCE_SANS_PERTE * len(avec_perte):
        return sans_perte, 'sans perte'
    return avec_perte, 'q90'


def traiter(chemin):
    source = open(chemin, encoding='utf-8').read()
    trouve = MANIFESTE.search(source)
    if not trouve:
        print(f"{chemin} : pas de manifeste, ignoré")
        return 0, 0
    manifeste = json.loads(trouve.group(2))

    for uuid, entree in manifeste.items():
        # Uniquement les PNG : relancer le script sur une page déjà allégée
        # ne doit pas ré-encoder du WebP en WebP (perte à chaque passage).
        if entree['mime'] != 'image/png' or entree.get('compressed'):
            continue
        png = base64.b64decode(entree['data'])
        webp, methode = alleger(png, uuid)
        if len(webp) >= len(png):
            print(f"  {uuid[:8]} conservé tel quel ({len(png) / 1e3:.1f} ko)")
            continue
        entree['data'] = base64.b64encode(webp).decode('ascii')
        entree['mime'] = 'image/webp'
        print(f"  {uuid[:8]} {len(png) / 1e3:8.1f} ko → {len(webp) / 1e3:7.1f} ko"
              f"  ({methode})")

    resultat = (source[:trouve.start()] + trouve.group(1)
                + json.dumps(manifeste, separators=(',', ':'), ensure_ascii=False)
                + trouve.group(3) + source[trouve.end():])
    open(chemin, 'w', encoding='utf-8').write(resultat)
    avant, apres = len(source), len(resultat)
    print(f"{chemin} : {avant / 1e6:.2f} Mo → {apres / 1e6:.2f} Mo "
          f"(−{100 * (1 - apres / avant):.0f} %)\n")
    return avant, apres


def main(chemins):
    if not chemins:
        print(__doc__)
        return 1
    avant = apres = 0
    for chemin in chemins:
        a, b = traiter(chemin)
        avant += a
        apres += b
    if avant:
        print(f"TOTAL {avant / 1e6:.2f} Mo → {apres / 1e6:.2f} Mo "
              f"(−{100 * (1 - apres / avant):.0f} %)")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
