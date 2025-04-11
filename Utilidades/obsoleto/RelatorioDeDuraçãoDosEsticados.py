import subprocess
from pathlib import Path
import re
import csv

pastas = {
    "C02": Path("videos_sincronizados/C02"),
    "C03": Path("videos_sincronizados/C03"),
    "C04": Path("videos_sincronizados/C04"),
}

def get_duracao(video_path):
    try:
        result = subprocess.check_output([
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", str(video_path)
        ], stderr=subprocess.DEVNULL)
        import json
        data = json.loads(result)
        return float(data["format"]["duration"])
    except Exception:
        return None  # Retorna None silenciosamente se corrompido ou ilegível


videos = {}
for key, pasta in pastas.items():
    for arquivo in pasta.glob(f"{key}_corte_*.mkv"):
        match = re.search(r"_(\d{3,4})\.mkv$", arquivo.name)
        if match:
            idx = match.group(1)
            videos.setdefault(idx, {})[key] = arquivo

linhas = []
for idx in sorted(videos.keys()):
    grupo = videos[idx]
    if len(grupo) < 2:
        continue

    duracoes = {k: get_duracao(v) for k, v in grupo.items()}
    dur_validas = {k: v for k, v in duracoes.items() if v is not None}

    if len(dur_validas) < 2:
        continue

    d_max = max(dur_validas.values())
    d_min = min(dur_validas.values())
    diff = d_max - d_min

    linha = [
        idx,
        f"{duracoes.get('C02', ''):.2f}" if duracoes.get("C02") else "",
        f"{duracoes.get('C03', ''):.2f}" if duracoes.get("C03") else "",
        f"{duracoes.get('C04', ''):.2f}" if duracoes.get("C04") else "",
        f"{diff:.2f}",
        max(dur_validas, key=dur_validas.get),
        min(dur_validas, key=dur_validas.get),
    ]
    linhas.append(linha)

csv_path = Path("relatorio_sincronizacao.csv")
with csv_path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Corte", "Duração_C02", "Duração_C03", "Duração_C04", "Diferença_Segundos", "Maior", "Menor"])
    writer.writerows(linhas)

print(f"✅ Relatório gerado com {len(linhas)} cortes válidos → {csv_path.resolve()}")
