import os
import cv2
import numpy as np

# Defina a pasta de origem das imagens
pasta_origem = '.'

# Defina a pasta de destino das imagens transformadas
pasta_destino = 'transformadas'

# Crie a pasta de destino se não existir
if not os.path.exists(pasta_destino):
    os.makedirs(pasta_destino)

# Liste todas as imagens da pasta de origem
for arquivo in os.listdir(pasta_origem):
    if arquivo.endswith('.jpg') or arquivo.endswith('.png'):
        # Carregue a imagem
        imagem = cv2.imread(os.path.join(pasta_origem, arquivo))

        # Aplique a transformação nos pixels
        imagem_transformada = np.where(imagem > 45, 255, 0).astype(np.uint8)

        # Salve a imagem transformada
        nome_arquivo = os.path.splitext(arquivo)[0]
        nome_transformado = f"{nome_arquivo}_transformado.jpg"
        cv2.imwrite(os.path.join(pasta_destino, nome_transformado), imagem_transformada)

        print(f"Imagem {arquivo} transformada e salva como {nome_transformado}")
