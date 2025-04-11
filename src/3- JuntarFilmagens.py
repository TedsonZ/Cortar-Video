import subprocess
from pathlib import Path
import shutil
from datetime import datetime
import os
from multiprocessing import Pool, cpu_count
from time import time

# 🕒 Marcar início
inicio_execucao = time()

# Pastas de entrada
pastas = {
    "C02": Path("C02_cortes_ffmpeg"),
    "C03": Path("C03_cortes_ffmpeg"),
    "C04": Path("C04_cortes_ffmpeg"),
}

saida_base = Path("videos_sincronizados")
saida_final = Path("video_final_rapido")
saida_final.mkdir(exist_ok=True)
for nome in pastas:
    (saida_base / nome).mkdir(parents=True, exist_ok=True)

# Listar arquivos ordenados
arquivos = {
    k: sorted(v.glob(f"{k}_corte_*.mkv"))
    for k, v in pastas.items()
}
total = min(len(arquivos["C02"]), len(arquivos["C03"]), len(arquivos["C04"]))
print(f"🔎 Processando {total} cortes...")

# Função para obter duração
def get_duracao(video_path):
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video_path)
        ]
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
        return float(output)
    except Exception:
        return 0.0

# 🔄 Pré-calcular todas as tarefas de sincronização
tarefas_sincronizacao = []
for i in range(total):
    trio = {
        "C02": arquivos["C02"][i],
        "C03": arquivos["C03"][i],
        "C04": arquivos["C04"][i],
    }
    duracoes = {k: get_duracao(v) for k, v in trio.items()}
    dur_max = max(duracoes.values())
    for k, v in trio.items():
        tarefas_sincronizacao.append((k, v, duracoes[k], dur_max))

# Função para sincronizar 1 vídeo
def sincronizar_video(tupla):
    k, video_path, dur, dur_max = tupla
    output_path = saida_base / k / video_path.name

    try:
        if abs(dur - dur_max) < 2.1:
            shutil.copy2(video_path, output_path)
        else:
            factor = dur_max / dur
            cmd = [
                "ffmpeg", "-y",
                "-i", str(video_path),
                "-filter_complex", f"[0:v]setpts={factor}*PTS[v]",
                "-map", "[v]", "-an",
                str(output_path)
            ]
            print(f"🎮 Esticando {video_path.name} com fator {factor:.3f} -> {k}")
            subprocess.run(cmd, check=True)

        # 🧹 Remover original após uso
        os.remove(video_path)
    except Exception as e:
        print(f"⚠️ Erro ao processar {video_path}: {e}")

# 🔁 Paralelizar sincronização com Pool
with Pool(processes=min(cpu_count(), 6)) as pool:
    pool.map(sincronizar_video, tarefas_sincronizacao)

print("✅ Todos os vídeos foram sincronizados!")

# 🎞️ Montagem final em paralelo
def montar_video_final(i):
    try:
        input_c02 = saida_base / "C02" / arquivos["C02"][i].name
        input_c03 = saida_base / "C03" / arquivos["C03"][i].name
        input_c04 = saida_base / "C04" / arquivos["C04"][i].name

        nome_final = f"final_{i:03d}.mkv"
        output_path = saida_final / nome_final

        cmd = [
            "ffmpeg", "-y",
            "-i", str(input_c04),
            "-i", str(input_c02),
            "-i", str(input_c03),
            "-filter_complex",
            (
                "nullsrc=size=1920x1080 [base];"
                "[0:v]transpose=1,scale=608:1080 [c04];"
                "[1:v]scale=1312:540 [c02];"
                "[2:v]scale=1312:540 [c03];"
                "[base][c04]overlay=shortest=1:x=0:y=0[tmp1];"
                "[tmp1][c03]overlay=shortest=1:x=608:y=540[tmp2];"
                "[tmp2][c02]overlay=shortest=1:x=608:y=0 [v]"
            ),
            "-map", "[v]",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "23",
            "-threads", str(os.cpu_count() or 4),
            "-shortest",
            str(output_path)
        ]

        print(f"🚀 Renderizando vídeo final {i+1}/{total}: {output_path.name}")
        subprocess.run(cmd, check=True)

        # 🧹 Limpar sincronizados usados
        os.remove(input_c02)
        os.remove(input_c03)
        os.remove(input_c04)
    except Exception as e:
        print(f"❌ Falha no render final {i:03d}: {e}")

# 🔁 Paralelizar montagem final
with Pool(processes=min(cpu_count(), 4)) as pool:
    pool.map(montar_video_final, range(total))

print("✅ Todos os vídeos finais foram gerados!")

# ⏱️ Tempo total
fim_execucao = time()
duracao = fim_execucao - inicio_execucao
dur_str = str(datetime.utcfromtimestamp(duracao).strftime('%H:%M:%S'))

with open("log.txt", "w") as f:
    f.write(f"Tempo total de execução: {dur_str}\n")

print(f"🕒 Tempo total: {dur_str}")

