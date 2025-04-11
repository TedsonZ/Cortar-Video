import os
import cv2

# Defina as coordenadas da região a ser recortada
CROP_REGION_C3 = (1070, 980, 202, 69)  # x, y, w, h

# Defina a pasta de origem das imagens
pasta_origem = 'paraCortar'

# Defina a pasta de destino das imagens recortadas
pasta_destino = 'recortados'

# Crie a pasta de destino se não existir
if not os.path.exists(pasta_destino):
    os.makedirs(pasta_destino)

# Liste todas as imagens da pasta de origem
for arquivo in os.listdir(pasta_origem):
    if arquivo.endswith('.jpg') or arquivo.endswith('.png'):
        # Carregue a imagem
        imagem = cv2.imread(os.path.join(pasta_origem, arquivo))

        # Recorte a região especificada
        x, y, w, h = CROP_REGION_C3
        recorte = imagem[y:y+h, x:x+w]

        # Salve a imagem recortada com um nome diferente
        nome_arquivo = os.path.splitext(arquivo)[0]
        nome_recorte = f"{nome_arquivo}.jpg"
        cv2.imwrite(os.path.join(pasta_destino, nome_recorte), recorte)

        print(f"Imagem {arquivo} recortada e salva como {nome_recorte}")
