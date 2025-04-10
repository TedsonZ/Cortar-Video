from pathlib import Path

# Caminhos
pasta_videos = Path("video_final_rapido")
arquivo_cortes = Path("cortes3.txt")

# Leitura dos textos dos cortes
linhas = arquivo_cortes.read_text(encoding="utf-8").splitlines()
textos = [linha.split(";")[0].strip().replace(" ", "_") for linha in linhas]

# Prefixo opcional
prefixo = input("🔤 Digite um prefixo para os arquivos (ou pressione ENTER para nenhum): ").strip()

# Renomear vídeos
for i, video in enumerate(sorted(pasta_videos.glob("final_*.mkv"))):
    try:
        texto = textos[i]
    except IndexError:
        texto = "sem_texto"

    novo_nome = f"{i:02}_{prefixo}_{texto}.mkv" if prefixo else f"{i:03}_{texto}.mkv"
    novo_caminho = pasta_videos / novo_nome

    video.rename(novo_caminho)
    print(f"✅ {video.name} → {novo_nome}")

print("\n✅ Renomeação concluída.")

