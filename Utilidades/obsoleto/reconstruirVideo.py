import os
import csv
import cv2
import shutil
from datetime import datetime, timedelta
from collections import defaultdict

# === CONFIG ===
FRAME_DIR = 'frames'
OUTPUT_DIR = 'frames_preenchidos'
TIMESTAMP_CSV = 'timestamps.csv'
FPS = 30
OUTPUT_VIDEO = 'reconstruido.avi'

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

# === FUNÇÃO: Preencher segundos com menos frames ===
def fill_missing_frames(timestamps):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    per_second = defaultdict(list)
    for frame, ts in timestamps:
        second_key = ts.strftime('%H:%M:%S')
        per_second[second_key].append((frame, ts))

    filled_list = []
    for second, frames in sorted(per_second.items()):
        if len(frames) < FPS:
            last_frame = sorted(frames, key=lambda x: x[0])[-1][0]  # último frame do segundo
            missing = FPS - len(frames)
            print(f"[⚠️] {second}: {len(frames)} frames - preenchendo {missing} com {last_frame}")
            for i in range(missing):
                new_name = f"{second.replace(':', '-')}_fill_{i:02}.jpg"
                src = os.path.join(FRAME_DIR, last_frame)
                dst = os.path.join(OUTPUT_DIR, new_name)
                shutil.copy(src, dst)
                filled_list.append((new_name, second))
        for frame, ts in frames:
            shutil.copy(os.path.join(FRAME_DIR, frame), os.path.join(OUTPUT_DIR, frame))
            filled_list.append((frame, second))

    return sorted(filled_list, key=lambda x: x[1])

# === FUNÇÃO: Criar vídeo ===
def gerar_video(frame_list, output_path):
    if not frame_list:
        print("[❌] Nenhum frame para processar.")
        return

    sample_frame = cv2.imread(os.path.join(OUTPUT_DIR, frame_list[0][0]))
    height, width, _ = sample_frame.shape

    writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'MJPG'), FPS, (width, height))
    for fname, _ in frame_list:
        img = cv2.imread(os.path.join(OUTPUT_DIR, fname))
        writer.write(img)
    writer.release()
    print(f"[🎬] Vídeo salvo como: {output_path}")

# === MAIN ===
if __name__ == '__main__':
    print('[📥] Carregando timestamps...')
    timestamps = load_timestamps(TIMESTAMP_CSV)

    print('[🧪] Preenchendo frames ausentes...')
    frame_list = fill_missing_frames(timestamps)

    print('[🎞️] Gerando vídeo final...')
    gerar_video(frame_list, OUTPUT_VIDEO)

    print('[✅] Processo concluído.')

