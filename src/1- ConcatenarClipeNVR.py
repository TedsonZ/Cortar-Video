import subprocess
import shutil
import logging
from pathlib import Path
from collections import defaultdict

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(message)s")

def listar_arquivos_avi(base_dir: Path):
    return sorted([
        f for f in base_dir.iterdir()
        if f.is_file() and f.name.startswith("0") and f.suffix == ".avi"
    ])

def agrupar_por_camera(arquivos):
    grupos = defaultdict(list)
    for f in arquivos:
        camera = f.name.split("_")[0]
        grupos[camera].append(f)
    return grupos

def corrigir_timestamps(input_path: Path, output_path: Path):
    if output_path.exists():
        return
    logging.info(f"Corrigindo timestamps: {input_path.name}")
    subprocess.run([
        "ffmpeg", "-y",
        "-fflags", "+genpts",
        "-i", str(input_path),
        "-an",
        "-c", "copy",
        str(output_path)
    ], check=True)

def gerar_concat_list(arquivos, fixed_dir: Path, camera: str):
    concat_file = fixed_dir / f"{camera}_concat_list.txt"
    with concat_file.open("w") as f:
        for arquivo in arquivos:
            fixed_file = fixed_dir / f"{arquivo.name}_fixed.avi"
            f.write(f"file '{fixed_file.resolve()}'\n")
    return concat_file

def concatenar_videos(concat_list: Path, output_path: Path):
    logging.info(f"Gerando vídeo final: {output_path.name}")
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        str(output_path)
    ], check=True)

def remover_arquivos(originais):
    for f in originais:
        try:
            f.unlink()
            logging.info(f"🗑️ Arquivo removido: {f.name}")
        except Exception as e:
            logging.warning(f"Não foi possível remover {f.name}: {e}")

def main():
    base_dir = Path.cwd()
    fixed_dir = base_dir / "fixed"
    fixed_dir.mkdir(exist_ok=True)

    avi_files = listar_arquivos_avi(base_dir)
    grupos = agrupar_por_camera(avi_files)

    for camera, arquivos in grupos.items():
        for arquivo in arquivos:
            entrada = base_dir / arquivo
            saida = fixed_dir / f"{arquivo.name}_fixed.avi"
            corrigir_timestamps(entrada, saida)

    for camera, arquivos in grupos.items():
        concat_list = gerar_concat_list(arquivos, fixed_dir, camera)
        output_final = base_dir / f"C{camera}.mkv"

        try:
            concatenar_videos(concat_list, output_final)
            remover_arquivos(arquivos)  # ⬅️ Apagar originais só após concatenação
        except subprocess.CalledProcessError:
            logging.error(f"❌ Falha ao concatenar vídeos da câmera {camera}. Arquivos originais mantidos.")

    if fixed_dir.exists():
        shutil.rmtree(fixed_dir)
        logging.info("🧹 Pasta temporária 'fixed' removida com sucesso.")

    logging.info("✅ Finalizado. Arquivos .avi convertidos, unificados e removidos com sucesso.")

if __name__ == "__main__":
    main()

