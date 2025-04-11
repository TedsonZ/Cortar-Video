
from PIL import Image

def extrair_regiao(x, y, largura, altura):
    # Abre a imagem
    img = Image.open('img_03.png')

    # Verifica se as coordenadas estão dentro da imagem
    if x < 0 or y < 0 or x + largura > img.width or y + altura > img.height:
        print("Coordenadas inválidas.")
        return

    # Extrai a região retangular
    regiao = img.crop((x, y, x + largura, y + altura))

    # Salva a região como uma nova imagem
    regiao.save('corte.png')

    # Exibe a região extraída
    #Sregiao.show()

while True:
    x = int(input("Insira a coordenada x: "))
    y = int(input("Insira a coordenada y: "))
    largura = int(input("Insira a largura: "))
    altura = int(input("Insira a altura: "))

    extrair_regiao(x, y, largura, altura)
