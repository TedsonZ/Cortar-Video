from pathlib import Path
import subprocess
import shlex
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
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

def processar_corte(video_id, input_path, output_dir, i, linha, usar_legenda):
    texto, inicio, fim = linha.strip().split(";")
    start = parse_time(inicio)
    end = parse_time(fim)
    duration = end - start
    nome_saida = f"{video_id}_corte_{i:03}.mkv"
    output_video = output_dir / nome_saida

    if video_id == "C03" and usar_legenda:
        # Gerar legenda temporária
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
        cmd = f"""ffmpeg -y -loglevel error -ss {inicio} -t {duration.total_seconds()} -i {shlex.quote(str(input_path))} -vf "ass={shlex.quote(str(temp_ass))}" -c:v libx264 -preset ultrafast -an {shlex.quote(str(output_video))}"""
    else:
        # Usar cópia direta para máxima performance
        cmd = f"""ffmpeg -y -loglevel error -ss {inicio} -t {duration.total_seconds()} -i {shlex.quote(str(input_path))} -c copy {shlex.quote(str(output_video))}"""

    print(f"🚀 [{video_id}] Corte {i:03} iniciado...")
    subprocess.run(cmd, shell=True, check=True)
    
    if video_id == "C03" and usar_legenda:
        temp_ass.unlink()

def processar_video(video_file, usar_legenda):
    input_path = Path(video_file)
    video_id = input_path.stem
    if not input_path.exists():
        print(f"❌ Vídeo {video_file} não encontrado. Pulando...")
        return

    cortes_file = Path(f"cortes{video_id[-1]}.txt")
    if not cortes_file.exists():
        print(f"❌ Arquivo de cortes {cortes_file} não encontrado. Pulando {video_id}...")
        return

    cortes = cortes_file.read_text(encoding="utf-8").splitlines()
    output_dir = Path(f"{video_id}_cortes_ffmpeg")
    if output_dir.exists():
        print(f"⏩ Pasta {output_dir} já existe. Pulando {video_file}.")
        return
    output_dir.mkdir()

    tasks = []
    with ThreadPoolExecutor() as executor:
        for i, linha in enumerate(cortes):
            task = executor.submit(processar_corte, video_id, input_path, output_dir, i, linha, usar_legenda)
            tasks.append(task)

        for future in as_completed(tasks):
            try:
                future.result()
            except subprocess.CalledProcessError as e:
                print(f"❌ Erro ao processar corte: {e}")

# 🎬 INÍCIO DO SCRIPT
if __name__ == "__main__":
    print("💬 Deseja adicionar legendas aos cortes de C03? (s/N): ", end="")
    usar_legenda_input = input().strip().lower()
    usar_legenda = usar_legenda_input == "s"

    print("💬 Deseja deletar os arquivos originais Cx.mkv após o processamento? (s/N): ", end="")
    deletar_mkvs_input = input().strip().lower()
    deletar_mkvs = deletar_mkvs_input == "s"

    # 🎥 Vídeos a processar
    videos = ["C02.mkv", "C03.mkv", "C04.mkv"]

    for v in videos:
        processar_video(v, usar_legenda)

    print("✅ Conversão finalizada.")
    gerar_relatorio_de_duração_dos_filmes()

    if deletar_mkvs:
        for v in videos:
            caminho = Path(v)
            if caminho.exists():
                caminho.unlink()
                print(f"🗑️ Arquivo deletado: {v}")

