import numpy as np, json, csv, os

N = 30
W = np.zeros((N, N))
for a in range(N):
    for b in range(a+1, N):
        d = b - a
        count = 0
        for c in range(N):
            for e in range(c+1, N):
                if e - c == d and (c != a or e != b):
                    count += 1
        if count > 0:
            W[a,b] = count
            W[b,a] = count

D = np.diag(W.sum(axis=1))
L = D - W
eps = 0.1
K = -(L + eps * np.eye(N))
K = np.round(K, 1)

# 1. CSV
with open('sidon_K30.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    for row in K:
        writer.writerow(row.tolist())
sz = os.path.getsize('sidon_K30.csv')
print(f"CSV: {sz} bytes")

# 2. Parquet
try:
    import pandas as pd
    df = pd.DataFrame(K, columns=[f'c{i}' for i in range(N)])
    df.to_parquet('sidon_K30.parquet', index=False)
    sz = os.path.getsize('sidon_K30.parquet')
    print(f"Parquet: {sz} bytes")
except Exception as e:
    print(f"Parquet failed: {e}")

# 3. NumPy .npy
np.save('sidon_K30_matrix.npy', K)
sz = os.path.getsize('sidon_K30_matrix.npy')
print(f"NPY: {sz} bytes")

# 4. JSON dict format
json_dict = {'dimension': N, 'matrix': K.tolist(), 'format': 'dense', 'epsilon': eps}
with open('sidon_K30_dict.json', 'w') as f:
    json.dump(json_dict, f)
sz = os.path.getsize('sidon_K30_dict.json')
print(f"JSON dict: {sz} bytes")

# 5. TSV
with open('sidon_K30.tsv', 'w', newline='') as f:
    writer = csv.writer(f, delimiter='\t')
    for row in K:
        writer.writerow(row.tolist())
sz = os.path.getsize('sidon_K30.tsv')
print(f"TSV: {sz} bytes")

# 6. Also generate larger matrices for limit testing
for n in [50, 100, 200, 500]:
    W2 = np.zeros((n, n))
    for a in range(n):
        for b in range(a+1, n):
            d2 = b - a
            count2 = 0
            for c2 in range(n):
                for e2 in range(c2+1, n):
                    if e2 - c2 == d2 and (c2 != a or e2 != b):
                        count2 += 1
            if count2 > 0:
                W2[a,b] = count2
                W2[b,a] = count2
    D2 = np.diag(W2.sum(axis=1))
    L2 = D2 - W2
    K2 = -(L2 + eps * np.eye(n))
    K2 = np.round(K2, 1)
    data = K2.tolist()
    fname = f'sidon_K{n}_inline.json'
    with open(fname, 'w') as f:
        json.dump(data, f)
    sz = os.path.getsize(fname)
    print(f"N={n} inline JSON: {sz} bytes ({sz/1024:.1f} KB)")

print("\nAll formats generated.")
