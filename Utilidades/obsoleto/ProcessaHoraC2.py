from PIL import Image
import cv2
import numpy as np

def processar_imagem(img):
    # Converter a imagem PIL para numpy
    img_np = np.array(img)
    
    # Processar a imagem
    pixels = img.load()
    min_r, max_r = 218, 255
    min_g, max_g = 218, 255
    min_b, max_b = 218, 255
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            r, g, b = pixels[x, y]
            if (min_r <= r <= max_r and min_g <= g <= max_g and min_b <= b <= max_b):
                pixels[x, y] = (0, 0, 0)
            else:
                pixels[x, y] = (255, 255, 255)

    # Converter a imagem para numpy novamente
    img_np = np.array(img)
    
    # Aplicar filtros
    img_gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    suave = cv2.GaussianBlur(img_gray, (5, 5), 1.2)
    final = cv2.adaptiveThreshold(suave, 255,
                                  cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                  cv2.THRESH_BINARY, 11, 2)

    # Retornar a imagem processada
    return final
