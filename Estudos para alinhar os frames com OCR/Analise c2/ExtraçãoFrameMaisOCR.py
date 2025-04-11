import cv2
import pytesseract
import os
import subprocess
from datetime import datetime
from PIL import Image, ImageEnhance, ImageOps
import csv
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from ProcessaHoraC2 import processar_imagem

# === CONFIG ===
VIDEO_FILE = 'C02.mkv'
FRAME_DIR = 'frames'
OUTPUT_CSV = 'timestamps.csv'
CROP_REGION = (980, 1025, 210, 55)  # x, y, w, h
THREADS = 15
RESIZE_SCALE = 0.5
MAX_ATTEMPTS = 20

import subprocess
import os

def converter_video_para_30fps(input_path, output_path=None):
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {input_path}")

    if output_path is None:
        base, _ = os.path.splitext(input_path)
        output_path = f"{base}_30fps.mkv"

    comando = [
        "ffmpeg",
        "-i", input_path,
        "-r", "30",                # define novo framerate
        "-c:v", "libx264",         # encoder de vídeo
        "-crf", "18",              # qualidade visual quase sem perdas
        "-preset", "slow",         # mais tempo, melhor compressão
        "-c:a", "copy",            # mantém áudio intacto
        output_path
    ]

    print(f"[🔄] Convertendo {input_path} para 30fps...")
    resultado = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if resultado.returncode != 0:
        print("[❌] Erro na conversão:")
        print(resultado.stderr.decode())
        return None

    print(f"[✅] Conversão concluída: {output_path}")
    return output_path


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
        x, y, w, h = CROP_REGION

        # Valida se a tupla de corte está correta
        if not all(isinstance(val, int) for val in (x, y, w, h)):
            raise ValueError(f"CROP_REGION mal definida: {CROP_REGION}")        
        cropped = img.crop((x, y, x + w, y + h))      


        for attempt in range(MAX_ATTEMPTS):
            enhanced = ImageOps.invert(cropped)
            contrast_factor = 2.0 + (attempt * 0.05)
            enhanced = ImageEnhance.Contrast(enhanced).enhance(contrast_factor)
            resized = enhanced.resize((int(w * RESIZE_SCALE), int(h * RESIZE_SCALE)), Image.LANCZOS)

            text = pytesseract.image_to_string(resized, config='--psm 7 -c tessedit_char_whitelist=0123456789:')
            cleaned = clean_ocr_text(text)
            match = re.search(r'\d{2}:\d{2}:\d{2}', cleaned)
            if match:
                timestamp = datetime.strptime(match.group(0), '%H:%M:%S')
                return image_path, timestamp, text

        return image_path, None, ''  # Retorno garantido mesmo sem sucesso no OCR
    except Exception as e:
        print(f'[!] Erro OCR {image_path}: {e}')
        return image_path, None, ''  # Garante retorno mesmo em erro
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def processarTodosFrames():
    print('[🚀] Iniciando processamento de todos os frames PNG...')

    frame_files = sorted([f for f in os.listdir(FRAME_DIR) if f.endswith('.png')])
    print(f'[📂] {len(frame_files)} arquivos PNG encontrados em {FRAME_DIR}')
    
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = {
            executor.submit(processar_e_salvar_regiao, os.path.join(FRAME_DIR, image_path)): image_path
            for image_path in frame_files
        }

        for idx, future in enumerate(as_completed(futures), 1):
            image_path = futures[future]
            try:
                resultado = future.result()
                if resultado:
                    print(f'[💾] ({idx}/{len(frame_files)}) Imagem salva: {resultado}')
                else:
                    print(f'[❌] ({idx}/{len(frame_files)}) Falha ao processar: {image_path}')
            except Exception as e:
                print(f'[💥] ({idx}/{len(frame_files)}) Exceção em {image_path}: {e}')

    total_time = time.time() - start_time
    print(f'[✅] Processamento completo em {total_time:.2f} segundos usando {THREADS} threads.')



def processar_e_salvar_regiao(image_path):
    try:
        img = Image.open(image_path).convert('RGB')
        x, y, w, h = CROP_REGION

        if not all(isinstance(val, int) for val in (x, y, w, h)):
            raise ValueError(f"CROP_REGION mal definida: {CROP_REGION}")

        # 🎯 Recortar região
        cropped0 = img.crop((x, y, x + w, y + h)) 

        # 🧪 Processar imagem (retorna np array)
        processed_np = processar_imagem(cropped0)

        # 🧩 Colar na imagem original
        processed_pil = Image.fromarray(processed_np).convert('RGB')
        img.paste(processed_pil, (x, y))

        # 💾 Salvar no mesmo local com .png
        save_path = os.path.splitext(image_path)[0] + '.png'
        img.save(save_path)

        return save_path  # retorna novo caminho

    except Exception as e:
        print(f'[❌] Erro ao processar e salvar: {image_path} → {e}')
        return None


# === FUNÇÃO: Extrair todos os frames ===
def extract_frames(video):
    os.makedirs(FRAME_DIR, exist_ok=True)
    subprocess.run([
        'ffmpeg', '-i', video, '-vsync', '0', '-qscale:v', '2', f'{FRAME_DIR}/frame_%06d.png'
    ])

import time  # Adiciona se ainda não tiver importado

# === FUNÇÃO: OCR em paralelo com threads ===
def process_all_frames():
    frame_files = sorted([f for f in os.listdir(FRAME_DIR) if f.endswith('.png')])
    full_paths = [os.path.join(FRAME_DIR, f) for f in frame_files]

    print(f'[🔎] Iniciando OCR em {len(full_paths)} imagens com {THREADS} threads...')
    start_time = time.time()  # ⏱️ Início do cronômetro

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = {executor.submit(try_ocr_with_enhancements, path): path for path in full_paths}
        with open(OUTPUT_CSV, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Frame', 'Timestamp', 'RawText'])

            for future in as_completed(futures):
                fname, timestamp, raw = future.result()
                writer.writerow([
                    os.path.basename(fname),
                    timestamp.strftime('%H:%M:%S') if timestamp else 'N/A',
                    raw
                ])
                print(f'[✔️] {os.path.basename(fname)} → {timestamp if timestamp else "Falha"}')

    total_time = time.time() - start_time  # ⏱️ Tempo total
    print(f'[✅] OCR finalizado em {total_time:.2f} segundos.')


# === MAIN ===
if __name__ == '__main__':
    print('[🧼] Limpando diretório de frames...')
    os.system(f'rm -rf {FRAME_DIR}')

    print('[📹] Convertendo video para 30fps...')
    VIDEO_FILE = converter_video_para_30fps(VIDEO_FILE)

    print('[📸] Extraindo frames do vídeo...')
    #extract_frames(VIDEO_FILE)

    print('[🖼️] Processando frames...')
    #processarTodosFrames()

    print('[🧠] Processando OCR...')
    #process_all_frames()

    print('[✅] Concluído! CSV salvo como timestamps.csv')
