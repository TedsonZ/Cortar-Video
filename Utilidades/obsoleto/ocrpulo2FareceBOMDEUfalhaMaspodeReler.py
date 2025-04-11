import cv2
import pytesseract
import os
import subprocess
from datetime import datetime
from PIL import Image, ImageEnhance
import csv
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# === CONFIG ===
VIDEO_FILE = 'C04.mkv'
FRAME_DIR = 'frames'
OUTPUT_CSV = 'timestamps.csv'
CROP_REGION = (1325, 925, 220, 100)  # x, y, w, h
THREADS = 18
RESIZE_SCALE = 2.5  # aumentar resolução para melhor OCR

# === FUNÇÃO: Limpeza do OCR ===
def clean_ocr_text(text):
    text = text.replace(' ', '').replace('\n', '')
    text = text.replace('O', '0').replace('I', '1').replace('l', '1')
    text = text.replace('S', '5').replace('B', '8')
    text = text.replace('T', '7').replace('Z', '2')
    text = text.replace('|', '1').replace('?', '7')
    text = re.sub(r'[^0-9:]', '', text)
    return text

# === FUNÇÃO: Ler hora via OCR ===
def read_time_from_image(image_path):
    try:
        img = Image.open(image_path)
        x, y, w, h = CROP_REGION
        cropped = img.crop((x, y, x + w, y + h)).convert('L')

        # Aumentar contraste e redimensionar
        cropped = ImageEnhance.Contrast(cropped).enhance(2.5)
        cropped = cropped.resize((int(w * RESIZE_SCALE), int(h * RESIZE_SCALE)), Image.LANCZOS)

        # OCR
        text = pytesseract.image_to_string(cropped, config='--psm 7 -c tessedit_char_whitelist=0123456789:')
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
    os.makedirs(FRAME_DIR, exist_ok=True)
    subprocess.run([
        'ffmpeg', '-i', video, '-vsync', '0', '-qscale:v', '2', f'{FRAME_DIR}/frame_%06d.jpg'
    ])

# === FUNÇÃO: OCR em paralelo com threads ===
def process_all_frames():
    frame_files = sorted([f for f in os.listdir(FRAME_DIR) if f.endswith('.jpg')])
    full_paths = [os.path.join(FRAME_DIR, f) for f in frame_files]

    print(f'[🔎] Iniciando OCR em {len(full_paths)} imagens com {THREADS} threads...')

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = {executor.submit(read_time_from_image, path): path for path in full_paths}
        with open(OUTPUT_CSV, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Frame', 'Timestamp', 'RawText'])

            for future in as_completed(futures):
                fname, timestamp, raw = future.result()
                writer.writerow([os.path.basename(fname), timestamp.strftime('%H:%M:%S') if timestamp else 'N/A', raw])
                print(f'[✔️] {os.path.basename(fname)} → {timestamp if timestamp else "Falha"}')

# === MAIN ===
if __name__ == '__main__':
    print('[🧼] Limpando diretório de frames...')
    #os.system(f'rm -rf {FRAME_DIR}')

    print('[📸] Extraindo frames do vídeo...')
    #extract_frames(VIDEO_FILE)

    print('[🧠] Processando OCR...')
    process_all_frames()

    print('[✅] Concluído! CSV salvo como timestamps.csv')

