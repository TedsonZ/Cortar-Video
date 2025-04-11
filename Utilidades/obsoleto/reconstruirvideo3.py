import os
import csv
import shutil
import time
from datetime import datetime, timedelta
from collections import defaultdict

# === CONFIG ===
FRAME_DIR = 'frames'
OUTPUT_DIR = 'frames_preenchidos'
TIMESTAMP_CSV = 'timestamps.csv'
FPS = 29
OUTPUT_VIDEO = 'reconstruido.mkv'  # Usar MKV como saída

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
        second_key = ts.replace(microsecond=0)  # Use datetime completo sem microssegundos
        per_second[second_key].append((frame, ts))

    filled_list = []
    for second, frames in sorted(per_second.items()):
        if len(frames) < FPS:
            last_frame = sorted(frames, key=lambda x: x[1])[-1][0]  # último frame com base no tempo
            missing = FPS - len(frames)
            print(f"[⚠️] {second.strftime('%H:%M:%S')}: {len(frames)} frames - preenchendo {missing} com {last_frame}")
            for i in range(missing):
                new_time = second + timedelta(milliseconds=999)  # Força a ficar no final do segundo
                new_name = f"{second.strftime('%H-%M-%S')}_fill_{i:02}.jpg"
                src = os.path.join(FRAME_DIR, last_frame)
                dst = os.path.join(OUTPUT_DIR, new_name)
                shutil.copy(src, dst)
                filled_list.append((new_name, new_time))
        for frame, ts in sorted(frames, key=lambda x: x[1]):
            shutil.copy(os.path.join(FRAME_DIR, frame), os.path.join(OUTPUT_DIR, frame))
            filled_list.append((frame, ts))

    return sorted(filled_list, key=lambda x: x[1])

# === FUNÇÃO: Criar vídeo com FFmpeg ===
def gerar_video_ffmpeg(frame_list, output_path):
    list_file = 'frame_list.txt'
    with open(list_file, 'w') as f:
        for frame, _ in frame_list:
            f.write(f"file '{os.path.join(OUTPUT_DIR, frame)}'\n")

    # Compressão eficiente usando H.264 (libx264) com framerate explícito
    cmd = f"ffmpeg -y -f concat -safe 0 -i {list_file} -framerate {FPS} -c:v libx264 -preset fast -crf 18 {output_path}"
    print(f"[🔧] Executando: {cmd}")
    os.system(cmd)
    print(f"[🎬] Vídeo final salvo como: {output_path}")

# === MAIN ===
if __name__ == '__main__':
    start_time = time.time()

    print('[📥] Carregando timestamps...')
    timestamps = load_timestamps(TIMESTAMP_CSV)

    print('[🧪] Preenchendo frames ausentes...')
    frame_list = fill_missing_frames(timestamps)

    print('[🎞️] Gerando vídeo final...')
    gerar_video_ffmpeg(frame_list, OUTPUT_VIDEO)

    elapsed = time.time() - start_time
    print(f'[✅] Processo concluído em {elapsed:.2f} segundos.')

