from pathlib import Path
import subprocess
import shlex
from datetime import datetime

input_video = "video.mkv"
output_dir = Path("cortes_ffmpeg")
output_dir.mkdir(exist_ok=True)

from datetime import timedelta

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


cortes = Path("cortes.txt").read_text(encoding="utf-8").splitlines()

for i, linha in enumerate(cortes):
    texto, inicio, fim = linha.strip().split(";")
    output_video = output_dir / f"corte_{i:03}.mkv"
    temp_ass = output_dir / f"temp_{i:03}.ass"

    start = parse_time(inicio)
    end = parse_time(fim)
    duration = end - start

    # Gerar ASS
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

    # Command
    cmd = f"""ffmpeg -y -loglevel error -ss {inicio} -t {duration.total_seconds()} -i {shlex.quote(input_video)} -vf "ass={shlex.quote(str(temp_ass))}" -c:v libx264 -preset ultrafast -an {shlex.quote(str(output_video))}"""


    print(f"Executando: {cmd}")
    subprocess.run(cmd, shell=True, check=True)

    temp_ass.unlink()

