from PIL import Image
import cv2
import numpy as np
import pytesseract
import os
import csv
import shutil
from concurrent.futures import ThreadPoolExecutor

input_dir = 'recortados'
output_dir = 'falhas'
output_input = 'falhas_input'
log_file = 'logOCR.csv'

os.makedirs(output_dir, exist_ok=True)
os.makedirs(output_input, exist_ok=True)

min_rgb = 215
max_rgb = 255
blur_kernel = (5, 5)
block_size = 13
c = 1

def preprocess_image(img):
    pixels = img.load()
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            r, g, b = pixels[x, y]
            if (min_rgb <= r <= max_rgb and min_rgb <= g <= max_rgb and min_rgb <= b <= max_rgb):
                pixels[x, y] = (0, 0, 0)
            else:
                pixels[x, y] = (255, 255, 255)
    img_np = np.array(img)
    img_gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    suave = cv2.GaussianBlur(img_gray, blur_kernel, 1.2)
    final = cv2.adaptiveThreshold(suave, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, c)
    return final

def extract_time_from_filename(filename):
    name = os.path.basename(filename)
    parts = name.split('_')[0].split('-')
    return f'{parts[0]}:{parts[1]}:{parts[2]}'

def process_image(image_path):
    expected = extract_time_from_filename(image_path)
    original = Image.open(image_path).convert('RGB')
    processed = preprocess_image(original.copy())
    ocr_text = pytesseract.image_to_string(processed, config='--psm 7').strip()
    success = expected == ocr_text
    if not success:
        fail_name = os.path.splitext(os.path.basename(image_path))[0] + '_falha.png'
        cv2.imwrite(os.path.join(output_dir, fail_name), processed)
        shutil.copy(image_path, os.path.join(output_input, os.path.basename(image_path)))
    return [os.path.basename(image_path), expected, ocr_text, success]

with ThreadPoolExecutor(max_workers=17) as executor:
    futures = []
    for file in os.listdir(input_dir):
        if file.lower().endswith('.jpg'):
            full_path = os.path.join(input_dir, file)
            futures.append(executor.submit(process_image, full_path))

    with open(log_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Arquivo', 'Esperado', 'Lido', 'Sucesso'])
        for future in futures:
            writer.writerow(future.result())

