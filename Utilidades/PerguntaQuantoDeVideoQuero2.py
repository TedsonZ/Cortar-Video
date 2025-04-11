import subprocess
import os

def extrair_video():
    # Lista os arquivos .mkv disponíveis
    arquivos_mkv = [f for f in os.listdir() if f.endswith('.mkv')]

    # Apresenta o menu de opção
    print("Selecione o arquivo .mkv que deseja extrair:")
    for i, arquivo in enumerate(arquivos_mkv):
        print(f"{i+1}. {arquivo}")

    # Pergunta a opção do usuário
    opcao = int(input("Digite o número do arquivo: "))

    # Verifica se a opção é válida
    if opcao < 1 or opcao > len(arquivos_mkv):
        print("Opção inválida.")
        return

    # Seleciona o arquivo escolhido
    arquivo_entrada = arquivos_mkv[opcao - 1]
    arquivo_saida = 'curto.mkv'

    # Pergunte a partir de quantos minutos e quanto de duração deseja extrair
    minutos_inicio = int(input("A partir de quantos minutos deseja extrair? "))
    segundos_inicio = minutos_inicio * 60
    duracao = int(input("Quanto tempo deseja extrair (em segundos)? "))

    # Formate o tempo de início e duração para o formato HH:MM:SS
    tempo_inicio = f"{segundos_inicio // 3600:02d}:{(segundos_inicio % 3600) // 60:02d}:{segundos_inicio % 60:02d}"
    tempo_duracao = f"{duracao // 3600:02d}:{(duracao % 3600) // 60:02d}:{duracao % 60:02d}"

    # Comando para extrair o trecho do vídeo
    comando_extrair_video = f'ffmpeg -threads 1 -i {arquivo_entrada} -ss {tempo_inicio} -t {tempo_duracao} -c:v copy {arquivo_saida}'

    try:
        # Executa o comando para extrair o vídeo
        subprocess.run(comando_extrair_video, shell=True, check=True)
        print(f"Vídeo {arquivo_saida} criado com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao criar o vídeo: {e}")

if __name__ == "__main__":
    extrair_video()