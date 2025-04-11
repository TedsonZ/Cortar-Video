from pathlib import Path
import subprocess
import re
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed

# 📁 Pastas contendo os cortes
pastas = {
    "C02": Path("C02_cortes_ffmpeg"),
    "C03": Path("C03_cortes_ffmpeg"),
    "C04": Path("C04_cortes_ffmpeg"),
}

# 🎥 Função para obter a duração via ffprobe
def get_duracao(video_path):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(video_path)
    ]
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
        return float(output)
    except subprocess.CalledProcessError:
        return None

def gerar_relatorio_de_duração_dos_filmes():
    # 🧪 Coletar arquivos por índice
    videos = {}
    for key, pasta in pastas.items():
        for arquivo in pasta.glob(f"{key}_corte_*.mkv"):
            match = re.search(r"_(\d{3})\.mkv$", arquivo.name)
            if match:
                idx = match[1]
                videos.setdefault(idx, {})[key] = arquivo

    # 📊 Resultados
    resultados = []

    def processar_corte(idx, grupo):
        if not all(k in grupo for k in ("C02", "C03", "C04")):
            return (idx, None)

        d_c02 = get_duracao(grupo["C02"])
        d_c03 = get_duracao(grupo["C03"])
        d_c04 = get_duracao(grupo["C04"])

        if None in (d_c02, d_c03, d_c04):
            return (idx, None)

        duracoes = {"C02": d_c02, "C03": d_c03, "C04": d_c04}
        max_d = max(duracoes.values())
        min_d = min(duracoes.values())
        diff = max_d - min_d
        maior = max(duracoes, key=duracoes.get)
        menor = min(duracoes, key=duracoes.get)

        return (idx, [idx, f"{d_c02:.2f}", f"{d_c03:.2f}", f"{d_c04:.2f}", f"{diff:.2f}", maior, menor], duracoes, diff, maior, menor)

    print("\n📊 Análise de Duração por Corte:")
    print("-" * 70)

    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(processar_corte, idx, grupo): idx
            for idx, grupo in videos.items()
        }

        for future in as_completed(futures):
            idx = futures[future]
            result = future.result()
            if result is None or result[1] is None:
                print(f"⚠️ Corte {idx}: erro ou arquivos ausentes.\n")
                continue

            idx, linha_csv, duracoes, diff, maior, menor = result
            print(f"🎞️ Corte {idx}:")
            for key in ("C02", "C03", "C04"):
                print(f"   📁 {key}: {duracoes[key]:.2f}s")
            print(f"   🔍 Desalinhamento: {diff:.2f}s (↑ {maior}, ↓ {menor})\n")
            resultados.append(linha_csv)

    # 📤 Exportar CSV
    csv_path = Path("desalinhamento_videos.csv")
    with csv_path.open("w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Corte", "Duração_C02", "Duração_C03", "Duração_C04", "Diferença_Segundos", "Maior", "Menor"])
        writer.writerows(resultados)

    print(f"✅ Relatório salvo em: {csv_path.resolve()}")

