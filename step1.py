# -*- coding: utf-8 -*-
import cv2
import sys

# Arguments pour le chemin de l'image d'entrée et de sortie
input_image_path = sys.argv[1]
output_image_path = sys.argv[2]

# Chargement de l'image d'entrée
image = cv2.imread(input_image_path)

# Conversion en niveaux de gris
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Inversion et flou pour obtenir l'effet esquisse
invert = cv2.bitwise_not(gray_image)
blur = cv2.GaussianBlur(invert, (21, 21), 0)
invertedBlur = cv2.bitwise_not(blur)
sketch = cv2.divide(gray_image, invertedBlur, scale=256.0)

# Sauvegarde de l'image finale
cv2.imwrite(output_image_path, sketch)
