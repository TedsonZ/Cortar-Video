import subprocess
import os

def extrair_video():
    # Defina o nome do arquivo de entrada e saída
    arquivo_entrada = input("Nome do Arquivo com extensão: ")
    arquivo_saida = 'curto.mkv'

    # Verifica se o arquivo de entrada existe
    if not os.path.exists(arquivo_entrada):
        print(f"O arquivo {arquivo_entrada} não existe.")
        return

    # Pergunte a partir de quantos minutos e quanto de duração deseja extrair
    minutos_inicio = int(input("A partir de quantos minutos deseja extrair? "))
    segundos_inicio = minutos_inicio * 60
    duracao = int(input("Quanto tempo deseja extrair (em segundos)? "))

    # Formate o tempo de início e duração para o formato HH:MM:SS
    tempo_inicio = f"{segundos_inicio // 3600:02d}:{(segundos_inicio % 3600) // 60:02d}:{segundos_inicio % 60:02d}"
    tempo_duracao = f"{duracao // 3600:02d}:{(duracao % 3600) // 60:02d}:{duracao % 60:02d}"

    # Comando para extrair o trecho do vídeo
    comando_extrair_video = f'ffmpeg -i {arquivo_entrada} -ss {tempo_inicio} -t {tempo_duracao} -c:v libx264 -crf 18 {arquivo_saida}'

    try:
        # Executa o comando para extrair o vídeo
        subprocess.run(comando_extrair_video, shell=True, check=True)
        print(f"Vídeo {arquivo_saida} criado com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao criar o vídeo: {e}")

def extrair_frames():
    # Defina o nome do arquivo de entrada
    arquivo_entrada = 'curto.mkv'

    # Verifica se o arquivo de entrada existe
    if not os.path.exists(arquivo_entrada):
        print(f"O arquivo {arquivo_entrada} não existe.")
        return

    # Comando para extrair 1 frame por segundo
    comando_extrair_frames = f'ffmpeg -i {arquivo_entrada} -vf fps=1 img_%02d.png'

    try:
        # Executa o comando para extrair os frames
        subprocess.run(comando_extrair_frames, shell=True, check=True)
        print("Frames extraídos com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao extrair os frames: {e}")

if __name__ == "__main__":
    extrair_video()
    #extrair_frames()
