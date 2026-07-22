from GHZ_CKA import *
import numpy as np
import matplotlib.pyplot as plt

# symmetric baseline: both arms at 0.3
q, c = ghz_circuit_asym([0.3, 0.3, 0.3], "phase")
qx, qz = qbers(q, c)
print("Symmetric [0.3, 0.3, 0.3]:  Q_X =", round(qx, 4))

# asymmetric: same TOTAL noise, spread unevenly
q, c = ghz_circuit_asym([0.0, 0.9, 0.0], "phase")
qx, qz = qbers(q, c)
print("Asymmetric [0.0, 0.9, 0.0]: Q_X =", round(qx, 4))


steps = np.linspace(0, 0.6, 25)
grid = np.zeros((len(steps), len(steps)))

for a in range(len(steps)):
    for b in range(len(steps)):
        q, c = ghz_circuit_asym([steps[a], steps[b], 0.0], "phase")
        qx, qz_list = qbers(q, c)
        rate = 1 - h(qx) - max(h(z) for z in qz_list) 
        grid[a][b] = max(0.0, rate)

plt.figure(figsize=(7, 6))
plt.imshow(grid, origin="lower", extent=[0, 0.6, 0, 0.6],
           aspect="auto", cmap="viridis")
plt.colorbar(label="GHZ key rate")
plt.xlabel("Noise on arm 2  (λ₂)")
plt.ylabel("Noise on arm 1  (λ₁)")
plt.title("Key rate vs. asymmetric arm noise (dephasing)")
plt.savefig("heatmap.png", dpi=150)
plt.show()