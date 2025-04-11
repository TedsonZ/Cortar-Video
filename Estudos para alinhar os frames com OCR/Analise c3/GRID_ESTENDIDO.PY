# Salve esse código como run_grid_extendido.py
from PIL import Image
import pytesseract
import cv2
import numpy as np
import os
import csv
from concurrent.futures import ThreadPoolExecutor

min_rgb_values = [195, 200, 205, 210]
max_rgb_values = [240, 245, 250, 255]
blur_sizes = [5, 7, 9]
block_sizes = [13, 15, 17, 19, 21, 23]
c_values = list(range(-5, 9))
input_folder = "falhas_input"
log_file = "logGRID_extendido.csv"

def process_image(file, min_rgb, max_rgb, blur, block_size, c_val):
    img_path = os.path.join(input_folder, file)
    img = Image.open(img_path).convert("RGB")
    pixels = img.load()
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            r, g, b = pixels[x, y]
            if min_rgb <= r <= max_rgb and min_rgb <= g <= max_rgb and min_rgb <= b <= max_rgb:
                pixels[x, y] = (0, 0, 0)
            else:
                pixels[x, y] = (255, 255, 255)
    img_np = np.array(img)
    img_gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    img_blur = cv2.GaussianBlur(img_gray, (blur, blur), 1.2)
    final = cv2.adaptiveThreshold(img_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, c_val)
    ocr_text = pytesseract.image_to_string(final, config='--psm 7').strip().replace(" ", "").replace("\n", "")
    expected = file.split("_")[0].replace("-", ":")
    return {
        "Filename": file,
        "MinRGB": min_rgb,
        "MaxRGB": max_rgb,
        "Blur": blur,
        "BlockSize": block_size,
        "C": c_val,
        "Expected": expected,
        "Read": ocr_text,
        "Success": ocr_text == expected
    }

def run_grid():
    os.makedirs("falhas_input", exist_ok=True)
    files = [f for f in os.listdir(input_folder) if f.endswith(".jpg")]
    all_results = []
    with ThreadPoolExecutor(max_workers=17) as executor:
        futures = []
        for file in files:
            for min_rgb in min_rgb_values:
                for max_rgb in max_rgb_values:
                    for blur in blur_sizes:
                        for block_size in block_sizes:
                            for c_val in c_values:
                                futures.append(executor.submit(
                                    process_image, file, min_rgb, max_rgb, blur, block_size, c_val))
        for f in futures:
            all_results.append(f.result())
    with open(log_file, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=all_results[0].keys())
        writer.writeheader()
        for row in all_results:
            writer.writerow(row)

if __name__ == "__main__":
    run_grid()
    print("Grid estendido finalizado. Resultados em logGRID_extendido.csv")

