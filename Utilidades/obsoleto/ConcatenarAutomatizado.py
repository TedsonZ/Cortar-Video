from pathlib import Path
import subprocess
import shlex
from datetime import datetime

# 📅 Entrada do usuário
entrada_data = input("📅 Digite a data e hora (dd-mm-yy_HH) ou pressione Enter para usar a atual: ").strip()

if entrada_data:
    try:
        data_exec = datetime.strptime(entrada_data, "%d%m%y%H")
        data_hora = data_exec.strftime("%d%m%y%H")
    except ValueError:
        print("❌ Formato inválido. Use: dd-mm-yy_HH (ex: 08042514)")
        exit(1)
else:
    now = datetime.now()
    data_hora = now.strftime("%d%m%y%H")

print(f"🧾 Data e hora definidas: {data_hora}")

# 📁 Pastas dos cortes
pastas = {
    "C02": Path("C02_cortes_ffmpeg"),
    "C03": Path("C03_cortes_ffmpeg"),
    "C04": Path("C04_cortes_ffmpeg"),
}

# 📄 Textos dos cortes
cortes_txt = Path("cortes.txt").read_text(encoding="utf-8").splitlines()
textos_dos_cortes = [linha.strip().split(";")[0] for linha in cortes_txt]

# 📁 Pasta de saída
output_dir = Path("video_final_rapido")
output_dir.mkdir(exist_ok=True)

# 🎞️ Arquivos
arquivos_c02 = sorted(pastas["C02"].glob("C02_corte_*.mkv"))
arquivos_c03 = sorted(pastas["C03"].glob("C03_corte_*.mkv"))
arquivos_c04 = sorted(pastas["C04"].glob("C04_corte_*.mkv"))

total = min(len(arquivos_c02), len(arquivos_c03), len(arquivos_c04), len(textos_dos_cortes))
print(f"🎬 Iniciando montagem de {total} vídeos finais...")

for i in range(total):
    input_c02 = arquivos_c02[i]
    input_c03 = arquivos_c03[i]
    input_c04 = arquivos_c04[i]

    # Nome do corte baseado no texto
    texto = textos_dos_cortes[i].strip().replace(" ", "_")
    nome_final = f"{data_hora}_{texto}.mkv"
    output_path = output_dir / nome_final

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(input_c04),
        "-i", str(input_c02),
        "-i", str(input_c03),
        "-filter_complex",
        """
        nullsrc=size=1920x1080 [base];
        [0:v]transpose=1,scale=608:1080 [c04];
        [1:v]scale=1312:540 [c02];
        [2:v]scale=1312:540 [c03];
        [base][c04]overlay=shortest=1:x=0:y=0[tmp1];
        [tmp1][c03]overlay=shortest=1:x=608:y=540[tmp2];
        [tmp2][c02]overlay=shortest=1:x=608:y=0 [v]
        """,
        "-map", "[v]",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "23",
        "-threads", "20",
        "-shortest",
        str(output_path)
    ]

    cmd = [part.strip() if isinstance(part, str) else part for part in cmd]

    print(f"🚀 Renderizando vídeo final {i+1}/{total}: {output_path.name}")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao processar {i}: {e}")

print("✅ Todos os vídeos finais foram gerados.")
