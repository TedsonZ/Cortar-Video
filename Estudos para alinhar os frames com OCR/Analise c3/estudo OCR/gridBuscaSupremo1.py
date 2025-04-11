
from PIL import Image
import cv2
import numpy as np
import pytesseract
import os
import csv
from concurrent.futures import ThreadPoolExecutor

input_dir = 'falhas_input'
log_file = 'logGRID.csv'

min_rgbs = [210, 215, 220]
max_rgb = 255
blur_kernels = [(3, 3), (5, 5)]
block_sizes = [11, 13, 15]
cs = [1, 2, 3]

def extract_expected(filename):
    parts = filename.split('_')[0].split('-')
    return f'{parts[0]}:{parts[1]}:{parts[2]}'

def preprocess(img, min_rgb, blur_kernel, block_size, c):
    pixels = img.load()
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            r, g, b = pixels[x, y]
            if (min_rgb <= r <= max_rgb and min_rgb <= g <= max_rgb and min_rgb <= b <= max_rgb):
                pixels[x, y] = (0, 0, 0)
            else:
                pixels[x, y] = (255, 255, 255)
    img_np = np.array(img)
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, blur_kernel, 1.2)
    return cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, c)

def test_config(file_path, min_rgb, blur_kernel, block_size, c):
    original = Image.open(file_path).convert('RGB')
    processed = preprocess(original.copy(), min_rgb, blur_kernel, block_size, c)
    ocr = pytesseract.image_to_string(processed, config='--psm 7').strip()
    expected = extract_expected(os.path.basename(file_path))
    success = ocr == expected
    return [os.path.basename(file_path), expected, ocr, success, min_rgb, blur_kernel[0], block_size, c]

def process_file(file_path):
    results = []
    for min_rgb in min_rgbs:
        for blur in blur_kernels:
            for block in block_sizes:
                for c_val in cs:
                    results.append(test_config(file_path, min_rgb, blur, block, c_val))
    return results

all_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.lower().endswith('.jpg')]

with ThreadPoolExecutor(max_workers=17) as executor:
    futures = [executor.submit(process_file, path) for path in all_files]

    with open(log_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Arquivo', 'Esperado', 'Lido', 'Sucesso', 'MinRGB', 'Blur', 'BlockSize', 'C'])
        for future in futures:
            for row in future.result():
                writer.writerow(row)

