import subprocess
import os

arquivo_entrada = input("Nome do Arquivo com extensão")
def extrair_video():
    # Defina o nome do arquivo de entrada e saída
    #arquivo_entrada = input("Nome do Arquivo com extensão")
    arquivo_saida = 'curto.mkv'

    # Verifica se o arquivo de entrada existe
    if not os.path.exists(arquivo_entrada):
        print(f"O arquivo {arquivo_entrada} não existe.")
        return

    # Comando para extrair os primeiros 5 segundos do vídeo
    comando_extrair_video = f'ffmpeg -i {arquivo_entrada} -ss 00:00:00 -t 5 -c:v libx264 -crf 18 {arquivo_saida}'

    try:
        # Executa o comando para extrair o vídeo
        subprocess.run(comando_extrair_video, shell=True, check=True)
        print(f"Vídeo {arquivo_saida} criado com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao criar o vídeo: {e}")

def extrair_frames():
    # Defina o nome do arquivo de entrada
    #arquivo_entrada = 'C04.mkv'

    # Verifica se o arquivo de entrada existe
    if not os.path.exists(arquivo_entrada):
        print(f"O arquivo {arquivo_entrada} não existe.")
        return

    # Comando para extrair 1 frame por segundo
    comando_extrair_frames = f'ffmpeg -i {arquivo_entrada} -ss 00:00:00 -t 5 -vf fps=1 img_%02d.png'

    try:
        # Executa o comando para extrair os frames
        subprocess.run(comando_extrair_frames, shell=True, check=True)
        print("Frames extraídos com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao extrair os frames: {e}")

if __name__ == "__main__":
    extrair_video()
    extrair_frames()
