import csv
from collections import defaultdict

resultados = defaultdict(lambda: {'total': 0, 'sucesso': 0})

with open('logGRID.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        key = (int(row['MinRGB']), int(row['Blur']), int(row['BlockSize']), int(row['C']))
        resultados[key]['total'] += 1
        if row['Sucesso'].lower() == 'true':
            resultados[key]['sucesso'] += 1

ranking = []
for params, stats in resultados.items():
    minrgb, blur, block, c = params
    total = stats['total']
    sucesso = stats['sucesso']
    perc = round((sucesso / total) * 100, 2)
    ranking.append((minrgb, blur, block, c, total, sucesso, perc))

ranking.sort(key=lambda x: (-x[5], -x[6]))

print("Top 10 configurações:")
for i, (minrgb, blur, block, c, total, sucesso, perc) in enumerate(ranking[:10], 1):
    print(f"{i}. Params: MinRGB={minrgb}, Blur={blur}x{blur}, Block={block}, C={c} → {sucesso}/{total} ({perc}%)")
