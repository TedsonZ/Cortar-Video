import csv
from collections import defaultdict

param_stats = defaultdict(lambda: {'ok': 0, 'fail': 0})

with open('logGRID.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        key = (
            int(row['MinRGB']),
            int(row['MaxRGB']),
            int(row['Blur']),
            int(row['BlockSize']),
            int(row['C'])
        )
        if row['Sucesso'].lower() == 'true':
            param_stats[key]['ok'] += 1
        else:
            param_stats[key]['fail'] += 1

sorted_results = sorted(param_stats.items(), key=lambda x: (-x[1]['ok'], x[1]['fail']))

print("Top configurações:\n")
for i, (params, stats) in enumerate(sorted_results[:10]):
    total = stats['ok'] + stats['fail']
    acc = stats['ok'] / total * 100
    print(f"{i+1}. Params: MinRGB={params[0]}, MaxRGB={params[1]}, Blur={params[2]}x{params[2]}, Block={params[3]}, C={params[4]} → {stats['ok']}/{total} ({acc:.2f}%)")

    if acc == 100.0:
        print("✅ Conjunto com 100% de acertos encontrado!")
        break

