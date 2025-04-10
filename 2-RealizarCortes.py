from pathlib import Path
import subprocess
import shlex
from datetime import timedelta
from RelatorioDeDuração import gerar_relatorio_de_duração_dos_filmes
def parse_time(t: str) -> timedelta:
    parts = t.strip().split(":")
    parts = [float(p) for p in parts]
    if len(parts) == 3:
        h, m, s = parts
    elif len(parts) == 2:
        h, m, s = 0, *parts
    elif len(parts) == 1:
        h, m, s = 0, 0, parts[0]
    else:
        raise ValueError(f"Formato de tempo inválido: {t}")
    return timedelta(hours=h, minutes=m, seconds=s)

# 🎥 Vídeos a processar
videos = ["C02.mkv", "C03.mkv", "C04.mkv"]

for video_file in videos:
    input_path = Path(video_file)
    video_id = input_path.stem  # C02, C03...

    if not input_path.exists():
        print(f"❌ Vídeo {video_file} não encontrado. Pulando...")
        continue

    # 📄 Determina o arquivo de cortes para cada vídeo
    cortes_file = Path(f"cortes{video_id[-1]}.txt")  # ex: cortesC2.txt
    if not cortes_file.exists():
        print(f"❌ Arquivo de cortes {cortes_file} não encontrado. Pulando {video_id}...")
        continue

    cortes = cortes_file.read_text(encoding="utf-8").splitlines()

    # 📁 Pasta de saída
    output_dir = Path(f"{video_id}_cortes_ffmpeg")
    if output_dir.exists():
        print(f"⏩ Pasta {output_dir} já existe. Pulando conversão de {video_file}.")
        continue
    output_dir.mkdir()

    for i, linha in enumerate(cortes):
        texto, inicio, fim = linha.strip().split(";")
        start = parse_time(inicio)
        end = parse_time(fim)
        duration = end - start

        nome_saida = f"{video_id}_corte_{i:03}.mkv"

        output_video = output_dir / nome_saida

        # 🎬 Comando base
        cmd = f"""ffmpeg -y -loglevel error -ss {inicio} -t {duration.total_seconds()} -i {shlex.quote(str(input_path))}"""

        # 💬 Se for C03, aplicar legenda com o texto
        if video_id == "C03":
            temp_ass = output_dir / f"temp_{i:03}.ass"
            ass_template = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, Alignment, MarginL, MarginR, MarginV, BorderStyle, Outline, Shadow, Encoding
Style: Default,Arial,150,&H00FFFFFF,&H00000000,&H64000000,0,0,5,10,10,10,1,2,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:09.00,Default,,0,0,0,,{texto}
"""
            temp_ass.write_text(ass_template, encoding="utf-8")
            cmd += f""" -vf "ass={shlex.quote(str(temp_ass))}" """

        # 🔄 Finaliza comando
        cmd += f""" -c:v libx264 -preset ultrafast -an {shlex.quote(str(output_video))}"""

        print(f"🚀 Executando para {video_id}: corte {i:03}")
        subprocess.run(cmd, shell=True, check=True)

        if video_id == "C03":
            temp_ass.unlink()

print("✅ Conversão finalizada.")

gerar_relatorio_de_duração_dos_filmes()

