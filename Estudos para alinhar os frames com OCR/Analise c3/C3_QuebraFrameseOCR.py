import cv2
import pytesseract
import os
import subprocess
from datetime import datetime
from PIL import Image, ImageEnhance, ImageOps
import csv
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

# === CONFIG ===

VIDEO_FILE_C3 = 'curto.mkv'
FRAME_DIR_C3 = 'framesC3'
#FRAME_DIR_C3 = 'copiados'
OUTPUT_CSV_C3 = 'timestampsC3.csv'
ANALYSIS_TXT_C3 = 'analise_C3.txt'
TIMESTAMP_CSV_C3 = OUTPUT_CSV_C3
CROP_REGION_C3 = (1070, 980, 202, 69)  # x, y, w, h


THREADS = 17
RESIZE_SCALE = 0.5  # reduzir resolução para imagens grandes
MAX_ATTEMPTS = 20


FPS = 29


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
    all_frames = sorted([f for f in os.listdir(FRAME_DIR_C3) if f.endswith('.jpg')])
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
    frame_counts = []
    for sec, frames in sorted(per_second.items()):
        count = len(frames)
        frame_counts.append(count)
        output.append(f"  {sec}: {count} frames")

    # Contagem de frames
    count_distribution = defaultdict(int)
    for count in frame_counts:
        count_distribution[count] += 1

    output.append("\n[📊] Distribuição de contagem de frames:")
    for count, freq in sorted(count_distribution.items()):
        output.append(f"  {count} frames: {freq} vezes")

    # Média
    average = sum(frame_counts) / len(frame_counts)
    output.append(f"\n[📊] Média de frames por segundo: {average:.2f}")

    # Números anormais
    outliers = [count for count in frame_counts if abs(count - FPS) > 5]
    if outliers:
        output.append("\n[🔍] Números anormais de frames:")
        for count in outliers:
            output.append(f"  {count} frames")
    else:
        output.append("\n[✅] Nenhum número anormal de frames.")

    return output

# === FUNÇÃO: Limpeza do OCR ===
def clean_ocr_text(text):
    text = text.replace(' ', '').replace('\n', '')
    text = text.replace('O', '0').replace('I', '1').replace('l', '1')
    text = text.replace('S', '5').replace('B', '8')
    text = text.replace('T', '7').replace('Z', '2')
    text = text.replace('|', '1').replace('?', '7')
    text = re.sub(r'[^0-9:]', '', text)
    return text

# === FUNÇÃO: Tentar OCR com ajustes ===
def try_ocr_with_enhancements(image_path):
    try:
        img = Image.open(image_path)
        x, y, w, h = CROP_REGION_C3
        cropped = img.crop((x, y, x + w, y + h)).convert('L')

        for attempt in range(MAX_ATTEMPTS):
            enhanced = ImageOps.invert(cropped)
            contrast_factor = 2.0 + (attempt * 0.05)
            enhanced = ImageEnhance.Contrast(enhanced).enhance(contrast_factor)
            resized = enhanced.resize((int(w * RESIZE_SCALE), int(h * RESIZE_SCALE)), Image.LANCZOS)

            text = pytesseract.image_to_string(resized, config='--psm 13 -c tessedit_char_whitelist=0123456789:')
            cleaned = clean_ocr_text(text)
            match = re.search(r'\d{2}:\d{2}:\d{2}', cleaned)
            if match:
                timestamp = datetime.strptime(match.group(0), '%H:%M:%S')
                return image_path, timestamp, text
    except Exception as e:
        print(f'[!] Erro OCR {image_path}: {e}')
    return image_path, None, ''

# === FUNÇÃO: Extrair todos os frames ===
def extract_frames(video):
    os.makedirs(FRAME_DIR_C3, exist_ok=True)
    subprocess.run([
        'ffmpeg', '-i', video, '-vsync', '0', '-qscale:v', '2', f'{FRAME_DIR_C3}/frame_%06d.jpg'
    ])

# === FUNÇÃO: OCR em paralelo com threads ===
def process_all_frames():
    frame_files = sorted([f for f in os.listdir(FRAME_DIR_C3) if f.endswith('.jpg')])
    full_paths = [os.path.join(FRAME_DIR_C3, f) for f in frame_files]

    print(f'[🔎] Iniciando OCR em {len(full_paths)} imagens com {THREADS} threads...')

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = {executor.submit(try_ocr_with_enhancements, path): path for path in full_paths}
        with open(OUTPUT_CSV_C3, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Frame', 'Timestamp', 'RawText'])

            for future in as_completed(futures):
                fname, timestamp, raw = future.result()
                writer.writerow([os.path.basename(fname), timestamp.strftime('%H:%M:%S') if timestamp else 'N/A', raw])
                print(f'[✔️] {os.path.basename(fname)} → {timestamp if timestamp else "Falha"}')

# === MAIN ===
if __name__ == '__main__':
    print('[🧼] Limpando diretório de frames...')
    os.system(f'rm -rf {FRAME_DIR_C3}')

    print('[📸] Extraindo frames do vídeo...')
    extract_frames(VIDEO_FILE_C3)

    print('[🧠] Processando OCR...')
    process_all_frames()

    print('[✅] Concluído! CSV salvo como timestamps.csv')

    print('[📥] Carregando timestamps...')
    timestamps = load_timestamps(TIMESTAMP_CSV_C3)

    print('[🧪] Analisando frames...')
    analysis = analyze_frames(timestamps)

    print('[💾] Salvando análise em arquivo...')
    with open(ANALYSIS_TXT_C3, 'w') as f:
        for line in analysis:
            f.write(line + '\n')

    print('[✅] Análise concluída.')

