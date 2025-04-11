import os
import subprocess
from collections import defaultdict

# Diretório atual
video_dir = os.getcwd()

# Agrupar arquivos por prefixo (ex: "02_", "03_")
video_groups = defaultdict(list)
for filename in os.listdir(video_dir):
    if filename.endswith(".avi") and "_" in filename:
        prefix = filename.split("_")[0]
        video_groups[prefix].append(filename)

# Processar cada grupo
for prefix, files in video_groups.items():
    # Ordenar os arquivos pelo timestamp na string
    sorted_files = sorted(files, key=lambda x: x.split("_", 2)[-1])

    # Criar arquivo de inputs para o ffmpeg
    input_txt = f"{prefix}_inputs.txt"
    with open(input_txt, "w") as f:
        for filename in sorted_files:
            f.write(f"file '{os.path.abspath(filename)}'\n")

    # Comando ffmpeg com -c copy e saída .mkv
    output_filename = f"{prefix}_concat.mkv"
    cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", input_txt,
        "-c", "copy",
        output_filename
    ]

    print(f"🔄 Concatenando grupo {prefix}...")
    subprocess.run(cmd)

    print(f"✅ Gerado: {output_filename}")
    os.remove(input_txt)  # Limpeza

print("🎉 Todos os grupos foram processados com sucesso!")

