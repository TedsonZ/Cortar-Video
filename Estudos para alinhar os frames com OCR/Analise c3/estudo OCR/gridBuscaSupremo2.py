import os
import cv2
import pytesseract
import numpy as np
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
import csv

input_folder = "falhas_input"
log_file = "logGRID.csv"

min_rgbs = [205, 210, 215, 220, 225]
max_rgbs = [240, 245, 250, 255]
blurs = [1, 3, 5, 7]
block_sizes = [9, 11, 13, 15, 17, 19]
c_values = [-3, -2, -1, 0, 1, 2, 3, 4, 5]

image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(".jpg")]

results = []

def process_image(filename, min_rgb, max_rgb, blur_k, block_size, c_val):
    path = os.path.join(input_folder, filename)
    pil_img = Image.open(path).convert("RGB")
    pixels = pil_img.load()
    for x in range(pil_img.size[0]):
        for y in range(pil_img.size[1]):
            r, g, b = pixels[x, y]
            if min_rgb <= r <= max_rgb and min_rgb <= g <= max_rgb and min_rgb <= b <= max_rgb:
                pixels[x, y] = (0, 0, 0)
            else:
                pixels[x, y] = (255, 255, 255)
    img_np = np.array(pil_img)
    img_gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    if blur_k > 1:
        img_gray = cv2.GaussianBlur(img_gray, (blur_k, blur_k), 1.2)
    thresh = cv2.adaptiveThreshold(
        img_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, block_size, c_val
    )
    text = pytesseract.image_to_string(thresh, config='--psm 7').strip()
    expected = filename.split("_")[0].replace("-", ":")
    sucesso = expected in text
    return {
        "Arquivo": filename,
        "MinRGB": min_rgb,
        "MaxRGB": max_rgb,
        "Blur": blur_k,
        "BlockSize": block_size,
        "C": c_val,
        "OCR": text,
        "Esperado": expected,
        "Sucesso": sucesso
    }

def run_grid_search():
    with ThreadPoolExecutor(max_workers=17) as executor:
        futures = []
        for min_rgb in min_rgbs:
            for max_rgb in max_rgbs:
                for blur in blurs:
                    for block_size in block_sizes:
                        for c in c_values:
                            for image_file in image_files:
                                futures.append(executor.submit(
                                    process_image, image_file, min_rgb, max_rgb, blur, block_size, c
                                ))
        for future in futures:
            results.append(future.result())
    with open(log_file, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Arquivo", "MinRGB", "MaxRGB", "Blur", "BlockSize", "C", "OCR", "Esperado", "Sucesso"
        ])
        writer.writeheader()
        for r in results:
            writer.writerow(r)

run_grid_search()
