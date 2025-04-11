import os
import csv
import shutil
import time
from datetime import datetime, timedelta
from collections import defaultdict

# === CONFIG ===

FRAME_DIR_C3 = 'framesC3'
OUTPUT_CSV_C3 = 'timestampsC3.csv'
ANALYSIS_TXT_C3 = 'analise_C3.txt'
CROP_REGION_C3 = (1070, 980, 202, 69)  # x, y, w, h


FRAME_DIR = FRAME_DIR_C3
OUTPUT_DIR = 'C3_frames_preenchidos'
RENAMED_DIR = 'C3_frames_renomeados'
TIMESTAMP_CSV = OUTPUT_CSV_C3
FPS = 29
OUTPUT_VIDEO = 'reconstruido_C3.mkv'  # Usar MKV como saída
USE_FAST_MODE = True  # << Toggle para ativar o modo rápido

# === FUNÇÃO: Extrair número do frame ===
def extract_frame_number(frame_name):
    try:
        return int(''.join(filter(str.isdigit, frame_name)))
    except:
        return 0

# === FUNÇÃO: Carregar CSV ===
def load_timestamps(csv_path):
    timestamps = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts_str = row['Timestamp']
            if ts_str != 'N/A':
                timestamps.append((row['Frame'], datetime.strptime(ts_str, '%H:%M:%S')))
    return sorted(timestamps, key=lambda x: (x[1], extract_frame_number(x[0])))

# === FUNÇÃO: Preencher segundos com menos frames ===
def fill_missing_frames(timestamps):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    per_second = defaultdict(list)

    # Agrupar frames por segundo
    for frame, ts in timestamps:
        second_key = ts.replace(microsecond=0)
        per_second[second_key].append((frame, ts))

    # Determinar intervalo completo de segundos
    all_seconds = sorted(per_second.keys())
    start_second = all_seconds[0]
    end_second = all_seconds[-1]
    current_second = start_second

    filled_list = []
    last_known_frame = None

    while current_second <= end_second:
        frames = per_second.get(current_second, [])
        if frames:
            # Temos frames reais nesse segundo
            last_known_frame = sorted(frames, key=lambda x: x[1])[-1][0]
            if len(frames) < FPS:
                missing = FPS - len(frames)
                print(f"[⚠️] {current_second.strftime('%H:%M:%S')}: {len(frames)} frames - preenchendo {missing} com {last_known_frame}")
                for i in range(missing):
                    new_time = current_second + timedelta(milliseconds=999)
                    new_name = f"{current_second.strftime('%H-%M-%S')}_fill_{i:02}.jpg"
                    src = os.path.join(FRAME_DIR, last_known_frame)
                    dst = os.path.join(OUTPUT_DIR, new_name)
                    shutil.copy(src, dst)
                    filled_list.append((new_name, new_time))
            # Copia os frames existentes
            for frame, ts in sorted(frames, key=lambda x: x[1]):
                shutil.copy(os.path.join(FRAME_DIR, frame), os.path.join(OUTPUT_DIR, frame))
                filled_list.append((frame, ts))
        else:
            # Nenhum frame nesse segundo → preencher completamente
            if last_known_frame is not None:
                print(f"[🚫] {current_second.strftime('%H:%M:%S')}: 0 frames - preenchendo 29 com {last_known_frame}")
                for i in range(FPS):
                    new_time = current_second + timedelta(milliseconds=(i * 1000 // FPS))
                    new_name = f"{current_second.strftime('%H-%M-%S')}_gapfill_{i:02}.jpg"
                    src = os.path.join(FRAME_DIR, last_known_frame)
                    dst = os.path.join(OUTPUT_DIR, new_name)
                    shutil.copy(src, dst)
                    filled_list.append((new_name, new_time))
            else:
                print(f"[❌] {current_second.strftime('%H:%M:%S')}: Sem frame anterior conhecido. Não foi possível preencher.")
        current_second += timedelta(seconds=1)

    return sorted(filled_list, key=lambda x: x[1])


# === FUNÇÃO: Renomear sequencialmente os frames ===
def renomear_sequencial(frame_list):
    os.makedirs(RENAMED_DIR, exist_ok=True)
    for i, (frame, _) in enumerate(frame_list):
        new_name = f"frame_{i:06}.jpg"
        shutil.copy(os.path.join(OUTPUT_DIR, frame), os.path.join(RENAMED_DIR, new_name))
    return RENAMED_DIR

# === FUNÇÃO: Criar vídeo com FFmpeg ===
def gerar_video_ffmpeg(frame_list, output_path):
    if USE_FAST_MODE:
        print("[⚡] Modo rápido ativado — renomeando frames...")
        input_dir = renomear_sequencial(frame_list)
        cmd = f"ffmpeg -y -framerate {FPS} -i {input_dir}/frame_%06d.jpg -c:v libx264 -preset veryfast -crf 18 {output_path}"
    else:
        list_file = 'frame_list.txt'
        with open(list_file, 'w') as f:
            for frame, _ in frame_list:
                f.write(f"file '{os.path.join(OUTPUT_DIR, frame)}'\n")
        cmd = f"ffmpeg -y -f concat -safe 0 -i {list_file} -c:v libx264 -preset fast -crf 18 -r {FPS} {output_path}"

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

