from GHZ_CKA import *
import numpy as np
import matplotlib.pyplot as plt

for N in [3, 4, 5]:
    print(f"N={N}: analytic crossover = {analytic_crossover(N):.3f}")

Ns = [3, 4, 5]

analytic = [analytic_crossover(N) for N in Ns]

simulated = [0.490, 0.410, 0.360]

plt.figure(figsize=(7, 5))
plt.plot(Ns, analytic, "-", linewidth = 2, label="Analytic", marker="o")
plt.plot(Ns, simulated, "o", markersize=10, label= "Simulated (Cirq)")
plt.xlabel("Group Size N")
plt.ylabel("Crossover noise strength λ")
plt.title("Dephasing crossover: theory vs simulation")
plt.grid(alpha=0.3)
plt.legend()
plt.xticks(Ns)
plt.savefig("validation.png", dpi=150)
plt.show()