import os
import subprocess
from collections import defaultdict

# Diretório atual
current_dir = os.getcwd()

# Filtrar arquivos .avi que começam com "0"
avi_files = sorted([
    f for f in os.listdir(current_dir)
    if f.startswith("0") and f.endswith(".avi")
])

# Agrupar por câmera (ex: "02")
camera_groups = defaultdict(list)
for f in avi_files:
    camera_prefix = f.split("_")[0]  # "02" de "02_R_..."
    camera_groups[camera_prefix].append(f)

# Caminho para arquivos temporários corrigidos
fixed_dir = os.path.join(current_dir, "fixed")
os.makedirs(fixed_dir, exist_ok=True)

# Corrigir timestamps e salvar arquivos temporários
for cam, files in camera_groups.items():
    for f in files:
        input_path = os.path.join(current_dir, f)
        output_path = os.path.join(fixed_dir, f"{f}_fixed.avi")
        if not os.path.exists(output_path):
            print(f"Corrigindo timestamps: {f}")
            subprocess.run([
                "ffmpeg", "-y",
                "-fflags", "+genpts",
                "-i", input_path,
                "-an",  # Remove áudio
                "-c", "copy",
                output_path
            ], check=True)

# Criar concat list por câmera e gerar MKV
for cam, files in camera_groups.items():
    concat_list_path = os.path.join(fixed_dir, f"{cam}_concat_list.txt")
    with open(concat_list_path, "w") as concat_file:
        for f in files:
            fixed_file = os.path.join(fixed_dir, f"{f}_fixed.avi")
            concat_file.write(f"file '{fixed_file}'\n")

    output_final = os.path.join(current_dir, f"C{cam}.mkv")
    print(f"Gerando arquivo final para câmera {cam}: {output_final}")

    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list_path,
        "-c", "copy",
        output_final
    ], check=True)

print("✅ Finalizado. Arquivos concatenados por câmera com timestamps corrigidos.")
# ⚠️ Remove a pasta 'fixed' após a concatenação final
import shutil

if os.path.exists("fixed"):
    shutil.rmtree("fixed")
    print("🧹 Pasta temporária 'fixed' removida com sucesso.")

