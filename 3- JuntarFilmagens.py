import subprocess
from pathlib import Path
import threading
from queue import Queue
from datetime import datetime
import os

# Pastas de entrada
pastas = {
    "C02": Path("C02_cortes_ffmpeg"),
    "C03": Path("C03_cortes_ffmpeg"),
    "C04": Path("C04_cortes_ffmpeg"),
}

# Pasta de saída sincronizada e final
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
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video_path)
        ]
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
        return float(output)
    except Exception:
        return 0.0

# Fila de tarefas
task_queue = Queue()

# Função para processar vídeos
def processar_video():
    while not task_queue.empty():
        k, video_path, dur, dur_max, i = task_queue.get()
        output_path = saida_base / k / video_path.name

        # Ignorar estiramento se diferença for menor que 1 segundo
        if abs(dur - dur_max) < 1.0:
            subprocess.run(["cp", str(video_path), str(output_path)])
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

        # 🧹 Apagar vídeo original da pasta C0X após uso
        try:
            os.remove(video_path)
        except Exception as e:
            print(f"⚠️ Falha ao remover original {video_path}: {e}")

        task_queue.task_done()

# Preencher a fila de tarefas
for i in range(total):
    trio = {
        "C02": arquivos["C02"][i],
        "C03": arquivos["C03"][i],
        "C04": arquivos["C04"][i],
    }
    duracoes = {k: get_duracao(v) for k, v in trio.items()}
    dur_max = max(duracoes.values())
    for k, v in trio.items():
        task_queue.put((k, v, duracoes[k], dur_max, i))

# Iniciar múltiplas threads
num_threads = 3  # Threads Python para esticar em paralelo
threads = []
for _ in range(num_threads):
    t = threading.Thread(target=processar_video)
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print("✅ Todos os vídeos foram sincronizados!")

# Montagem final dos vídeos
print("🎬 Iniciando montagem dos vídeos finais...")
for i in range(total):
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
        "-threads", "17",
        "-shortest",
        str(output_path)
    ]

    print(f"🚀 Renderizando vídeo final {i+1}/{total}: {output_path.name}")
    subprocess.run(cmd, check=True)

    # 🧹 Liberar espaço após renderizar
    try:
        os.remove(input_c02)
        os.remove(input_c03)
        os.remove(input_c04)
    except Exception as e:
        print(f"⚠️ Falha ao remover arquivos temporários: {e}")

print("✅ Todos os vídeos finais foram gerados!")

