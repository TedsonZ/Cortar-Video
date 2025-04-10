import os
import subprocess
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import csv
import re

def natural_sort_key(text):
    # Divide por números e letras para ordenar tipo Windows Explorer
    return [int(c) if c.isdigit() else c.lower() for c in re.split('([0-9]+)', text)]

def listar_videos(diretorio="."):
    arquivos = [f for f in os.listdir(diretorio) if f.endswith(".mkv")]
    return sorted(arquivos, key=natural_sort_key)

def exportar_csv_lista_videos(videos, nome_arquivo="lista_videos.csv"):
    with open(nome_arquivo, mode="w", newline='', encoding="utf-8") as arquivo:
        writer = csv.writer(arquivo)
        writer.writerow(["index", "nome_arquivo"])
        for idx, nome in enumerate(videos):
            writer.writerow([idx, nome])
    print(f"✅ Lista salva como: {nome_arquivo}")


def selecionar_video(videos):
    print("\n🎞️ Vídeos encontrados:")
    for idx, v in enumerate(videos):
        print(f"[{idx}] {v}")
    escolha = int(input("\nEscolha o número do vídeo: "))
    return videos[escolha]

def detectar_fps(video_path):
    comando = [
        "ffprobe",
        "-v", "0",
        "-select_streams", "v:0",
        "-show_entries", "stream=r_frame_rate",
        "-of", "csv=p=0",
        video_path
    ]
    resultado = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    taxa = resultado.stdout.strip()
    try:
        num, den = map(int, taxa.split("/"))
        fps = round(num / den)
        print(f"🎯 FPS detectado: {fps}")
        return fps
    except:
        print("⚠️ Não foi possível detectar o FPS. Usando padrão 30.")
        return 30

def parse_tempos(entrada):
    tempos = []
    for t in entrada.split(","):
        t = t.strip()
        if ":" in t:
            partes = t.split(":")
            minutos = int(partes[0])
            segundos = int(partes[1])
            total_seg = max(0, minutos * 60 + segundos - 1)
            tempo_str = t.replace(":", "_")
            tempos.append((tempo_str, total_seg))
    return tempos

def extrair_frames_ffmpeg(video_path, tempo_str, inicio_seg, fps):
    nome_video = Path(video_path).stem
    pasta_destino = Path(f"Frames_extraidos/{nome_video}/{tempo_str}")
    pasta_destino.mkdir(parents=True, exist_ok=True)

    comando = [
        "ffmpeg",
        "-loglevel", "error",
        "-ss", str(inicio_seg),
        "-i", video_path,
        "-t", "3",
        "-vf", f"fps={fps}",
        str(pasta_destino / f"{tempo_str}_%04d.png")
    ]

    print(f"🧪 Iniciando: {tempo_str}")
    subprocess.run(comando)
    print(f"✅ Finalizado: {tempo_str}")

def processo_video():
    videos = listar_videos()
    if not videos:
        print("Nenhum vídeo .mkv encontrado no diretório atual.")
        return False

    video_escolhido = selecionar_video(videos)
    fps = detectar_fps(video_escolhido)

    entrada = input("\nInforme tempos separados por vírgula (ex: 0:44,1:13): ")
    tempos = parse_tempos(entrada)

    with ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(extrair_frames_ffmpeg, video_escolhido, tempo_str, inicio_seg, fps)
            for tempo_str, inicio_seg in tempos
        ]
        for f in futures:
            f.result()
    return True

def main():
    videos = listar_videos()
    if not videos:
        print("Nenhum vídeo .mkv encontrado no diretório atual.")
        return

    exportar = input("Deseja exportar a lista de vídeos .mkv para CSV? (s/n): ")
    if exportar.lower() == "s":
        exportar_csv_lista_videos(videos)

    while True:
        ok = processo_video()
        if not ok:
            break
        cont = input("\nDeseja trabalhar com outro vídeo? (s/n): ")
        if cont.lower() != "s":
            break

if __name__ == "__main__":
    main()
