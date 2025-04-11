import subprocess

input_c04 = "C04.mkv"
input_c02 = "C02.mkv"
input_c03 = "C03.mkv"
output = "video_final_rapido.mp4"

cmd = [
    "ffmpeg",
    "-i", input_c04,
    "-i", input_c02,
    "-i", input_c03,
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
    "-threads", "auto",
    "-shortest",
    output
]

cmd = [part.strip() if isinstance(part, str) else part for part in cmd]

try:
    subprocess.run(cmd, check=True)
    print("✅ Render final concluído com sucesso:", output)
except subprocess.CalledProcessError as e:
    print("❌ Erro ao executar ffmpeg:", e)
