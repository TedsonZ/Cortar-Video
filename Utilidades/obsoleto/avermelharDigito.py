from PIL import Image

# Abrir a imagem
img = Image.open('corte.png')
pixels = img.load()

# Definir a faixa de tolerância para as cores
min_r, max_r = 218, 255
min_g, max_g = 218, 255
min_b, max_b = 218, 255

# Definir a cor vermelha
cor_vermelha = (255, 0, 0)

# Percorrer todos os pixels da imagem
for x in range(img.size[0]):
    for y in range(img.size[1]):
        pixel = pixels[x, y]
        # Verificar se o pixel está dentro da faixa de tolerância
        if (min_r <= pixel[0] <= max_r and
            min_g <= pixel[1] <= max_g and
            min_b <= pixel[2] <= max_b):
            # Se estiver, mudar o pixel para vermelho
            pixels[x, y] = cor_vermelha

# Salvar a imagem modificada
img.save('vermelho.png')
