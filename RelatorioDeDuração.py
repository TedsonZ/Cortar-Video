from pathlib import Path
import subprocess
import re
import csv

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
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode().strip()
        return float(output)
    except subprocess.CalledProcessError:
        return None

def gerar_relatorio_de_duração_dos_filmes():
    # 🧪 Coletar arquivos organizados por índice
    videos = {}
    for key, pasta in pastas.items():
        for arquivo in pasta.glob(f"{key}_corte_*.mkv"):
            match = re.search(r"_(\d{3})\.mkv$", arquivo.name)
            if match:
                idx = match.group(1)
                videos.setdefault(idx, {})[key] = arquivo

    # 📊 Lista de resultados
    resultados = []

    # 📊 Análise de desalinhamento
    print("\n📊 Análise de Duração por Corte:")
    print("-" * 70)

    for idx in sorted(videos.keys()):
        grupo = videos[idx]
        if all(k in grupo for k in ("C02", "C03", "C04")):
            d_c02 = get_duracao(grupo["C02"])
            d_c03 = get_duracao(grupo["C03"])
            d_c04 = get_duracao(grupo["C04"])

            if None in (d_c02, d_c03, d_c04):
                print(f"❌ Corte {idx}: erro ao ler duração de um ou mais arquivos.")
                continue

            duracoes = {"C02": d_c02, "C03": d_c03, "C04": d_c04}
            max_d = max(duracoes.values())
            min_d = min(duracoes.values())
            diff = max_d - min_d
            maior = max(duracoes, key=duracoes.get)
            menor = min(duracoes, key=duracoes.get)

            print(f"🎞️ Corte {idx}:")
            for key, dur in duracoes.items():
                print(f"   📁 {key}: {dur:.2f}s")
            print(f"   🔍 Desalinhamento: {diff:.2f}s (↑ {maior}, ↓ {menor})\n")

            resultados.append([
                idx, f"{d_c02:.2f}", f"{d_c03:.2f}", f"{d_c04:.2f}",
                f"{diff:.2f}", maior, menor
            ])
        else:
            print(f"⚠️ Corte {idx}: Arquivos ausentes, pulando...\n")

    # 📤 Exportar para CSV
    csv_path = Path("desalinhamento_videos.csv")
    with csv_path.open("w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Corte", "Duração_C02", "Duração_C03", "Duração_C04", "Diferença_Segundos", "Maior", "Menor"])
        writer.writerows(resultados)

    print(f"✅ Relatório salvo em: {csv_path.resolve()}")

