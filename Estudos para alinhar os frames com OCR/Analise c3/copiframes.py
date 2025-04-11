import os
import csv
import shutil

# Defina a pasta de origem das imagens
pasta_origem = 'framesC3'

# Defina a pasta de destino das imagens selecionadas
pasta_destino = 'frames_selecionados'

# Verifique se a pasta de origem existe
if not os.path.exists(pasta_origem):
    print(f"Pasta {pasta_origem} não encontrada")
    exit()

# Crie a pasta de destino se não existir
try:
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
except PermissionError:
    print(f"Permissão negada para criar a pasta {pasta_destino}")
    exit()

# Leia o arquivo CSV
try:
    with open('timestampsC3.csv', 'r') as arquivo:
        leitor = csv.reader(arquivo, delimiter=',')
        next(leitor)  # Pule a linha de cabeçalho
        horarios = {}
        for linha in leitor:
            linha = [x.strip() for x in linha]
            print(f"Linha: {linha}")
            if len(linha) < 3:
                print(f"Linha inválida: {linha}")
                continue
            horario = linha[1]
            if horario not in horarios:
                horarios[horario] = linha[0]
                # Copie o arquivo para a pasta de destino
                #nome_arquivo = f"{os.path.splitext(linha[0])[0]}_{horario.replace(':', '-')}.jpg"
                nome_arquivo = f"{horario.replace(':', '-')}_{linha[0]}"
                try:
                    shutil.copy(os.path.join(pasta_origem, linha[0]), os.path.join(pasta_destino, nome_arquivo))
                    print(f"Arquivo {linha[0]} copiado para {nome_arquivo}")
                except FileNotFoundError:
                    print(f"Arquivo {linha[0]} não encontrado na pasta {pasta_origem}")
                except PermissionError:
                    print(f"Permissão negada para copiar o arquivo {linha[0]} para a pasta {pasta_destino}")
except FileNotFoundError:
    print("Arquivo timestampsC3.csv não encontrado")
except PermissionError:
    print("Permissão negada para ler o arquivo timestampsC3.csv")