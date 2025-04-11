import os
import shutil

# Defina as pastas de origem e destino
pasta_origem = 'framesC3'
pasta_destino = 'copiados'

# Crie a pasta de destino se não existir
if not os.path.exists(pasta_destino):
    os.makedirs(pasta_destino)

# Leia as linhas do arquivo lista.txt
with open('lista.txt', 'r') as arquivo:
    for linha in arquivo:
        nome_arquivo = linha.strip()  # Remova o caractere de nova linha
        caminho_origem = os.path.join(pasta_origem, nome_arquivo)
        
        # Verifique se o arquivo existe na pasta de origem
        if os.path.exists(caminho_origem):
            caminho_destino = os.path.join(pasta_destino, nome_arquivo)
            shutil.copy(caminho_origem, caminho_destino)
            print(f"Arquivo {nome_arquivo} copiado com sucesso!")
        else:
            print(f"Arquivo {nome_arquivo} não encontrado na pasta de origem.")
