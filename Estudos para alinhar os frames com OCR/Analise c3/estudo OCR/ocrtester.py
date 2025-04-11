from PIL import Image
import cv2
import numpy as np
import pytesseract
import os
import csv
from concurrent.futures import ThreadPoolExecutor

input_dir = 'recortados'
output_dir = 'falhas'
log_file = 'logOCR.csv'

os.makedirs(output_dir, exist_ok=True)

rgb_ranges = [(215, 255), (220, 255), (225, 255)]
blur_kernels = [(3, 3), (5, 5)]
block_sizes = [9, 11, 13]
c_values = [1, 2, 3]

def preprocess_image(img, min_rgb, max_rgb, blur_kernel, block_size, c):
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
    results = []
    expected = extract_time_from_filename(image_path)
    original = Image.open(image_path).convert('RGB')
    for min_rgb, max_rgb in rgb_ranges:
        for blur_kernel in blur_kernels:
            for block_size in block_sizes:
                for c in c_values:
                    processed = preprocess_image(original.copy(), min_rgb, max_rgb, blur_kernel, block_size, c)
                    ocr_text = pytesseract.image_to_string(processed, config='--psm 7').strip()
                    success = expected == ocr_text
                    results.append([os.path.basename(image_path), expected, ocr_text, success, min_rgb, max_rgb, blur_kernel[0], block_size, c])
                    if not success:
                        fail_name = f"{os.path.splitext(os.path.basename(image_path))[0]}_{min_rgb}_{blur_kernel[0]}_{block_size}_{c}.png"
                        cv2.imwrite(os.path.join(output_dir, fail_name), processed)
    return results

with ThreadPoolExecutor(max_workers=17) as executor:
    futures = []
    for file in os.listdir(input_dir):
        if file.lower().endswith('.jpg'):
            full_path = os.path.join(input_dir, file)
            futures.append(executor.submit(process_image, full_path))

    with open(log_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Arquivo', 'Esperado', 'Lido', 'Sucesso', 'MinRGB', 'MaxRGB', 'Blur', 'BlockSize', 'C'])
        for future in futures:
            for row in future.result():
                writer.writerow(row)

