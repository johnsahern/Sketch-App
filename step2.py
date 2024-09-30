# -*- coding: utf-8 -*-
from PIL import Image
import sys

def appliquer_filtre(image_path, output_path, couleur):
    # Ouvrir l'image
    img = Image.open(image_path)

    # Convertir l'image en RGB
    img = img.convert("RGB")

    # Appliquer le filtre
    pixels = img.load()
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            r, g, b = img.getpixel((i, j))
            # Appliquer le filtre couleur par normalisation
            r = int(r * couleur[0] / 255)
            g = int(g * couleur[1] / 255)
            b = int(b * couleur[2] / 255)
            pixels[i, j] = (r, g, b)

    # Enregistrer l'image filtrée
    img.save(output_path)

if __name__ == "__main__":
    # Arguments pour le chemin de l'image d'entrée et de sortie
    input_image_path = sys.argv[1]
    output_image_path = sys.argv[2]

    # Appliquer le filtre de couleur argile foncé (RGB : 209, 199, 184)
    appliquer_filtre(input_image_path, output_image_path, (209, 199, 184))
