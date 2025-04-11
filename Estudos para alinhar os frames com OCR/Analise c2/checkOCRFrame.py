import os
import csv
from datetime import datetime
from collections import defaultdict

# === CONFIG ===
FRAME_DIR = 'frames'
TIMESTAMP_CSV = 'timestamps.csv'
FPS = 30
ANALYSIS_TXT = 'analise.txt'

# === FUNÇÃO: Carregar CSV ===
def load_timestamps(csv_path):
    timestamps = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts_str = row['Timestamp']
            if ts_str != 'N/A':
                timestamps.append((row['Frame'], datetime.strptime(ts_str, '%H:%M:%S')))
    return sorted(timestamps, key=lambda x: x[1])

# === FUNÇÃO: Verificar consistência ===
def analyze_frames(timestamps):
    all_frames = sorted([f for f in os.listdir(FRAME_DIR) if f.endswith('.jpg')])
    output = []

    output.append(f"[📁] Total de frames na pasta: {len(all_frames)}")
    output.append(f"[📄] Total de timestamps válidos no CSV: {len(timestamps)}")

    missing_frames = set(f for f, _ in timestamps).symmetric_difference(all_frames)
    if missing_frames:
        output.append(f"[⚠️] Frames inconsistentes encontrados: {len(missing_frames)}")
    else:
        output.append("[✅] Todos os frames do CSV existem na pasta.")

    # Agrupar por segundo
    per_second = defaultdict(list)
    for frame, ts in timestamps:
        second_key = ts.strftime('%H:%M:%S')
        per_second[second_key].append(frame)

    output.append("\n[📊] Distribuição de frames por segundo:")
    for sec, frames in sorted(per_second.items()):
        output.append(f"  {sec}: {len(frames)} frames")

    expected_per_sec = FPS
    outliers = {sec: len(frames) for sec, frames in per_second.items() if abs(len(frames) - expected_per_sec) > 5}
    if outliers:
        output.append("\n[🔍] Segundos com número anormal de frames:")
        for sec, count in outliers.items():
            output.append(f"  {sec}: {count} frames")
    else:
        output.append("\n[✅] Nenhum segundo com discrepância significativa.")

    return output

# === MAIN ===
if __name__ == '__main__':
    print('[📥] Carregando timestamps...')
    timestamps = load_timestamps(TIMESTAMP_CSV)

    print('[🧪] Analisando frames...')
    analysis = analyze_frames(timestamps)

    print('[💾] Salvando análise em arquivo...')
    with open(ANALYSIS_TXT, 'w') as f:
        for line in analysis:
            f.write(line + '\n')

    print('[✅] Análise concluída.')
