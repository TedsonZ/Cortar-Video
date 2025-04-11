import cv2
import pytesseract
from PIL import Image
import numpy as np
from pathlib import Path
from datetime import datetime

def carregar_imagem(caminho):
    return cv2.imread(str(caminho))

def padronizar_imagem(imagem):
    cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    return cinza

def ocr_imagem(imagem):
    return pytesseract.image_to_string(Image.fromarray(imagem), config='--psm 7 -c tessedit_char_whitelist=0123456789:').strip()

def salvar_imagem(imagem, nome_saida):
    cv2.imwrite(nome_saida, imagem)

pasta = Path('.')
for img_path in pasta.glob('*.png'):
    imagem = carregar_imagem(img_path)
    tratada = padronizar_imagem(imagem)
    texto = ocr_imagem(tratada)
    if texto:
        nome_saida = f"resultado_{texto.replace(':', '-')}.png"
        salvar_imagem(tratada, nome_saida)
