from GHZ_CKA import *
import numpy as np
import matplotlib.pyplot as plt

gammas = np.linspace(0.0, 0.6, 121)

ghz_rates = [ghz_key_rate(3, "phase", g) for g in gammas]
pw_rates = [pairwise_key_rate(3, "phase", g) for g in gammas]

plt.figure(figsize=(8, 5))
plt.plot(gammas, ghz_rates, label="GHZ conference", linewidth=2)
plt.plot(gammas, pw_rates, label="Pairwise BB84", linewidth=2, linestyle="--")
plt.xlabel("Noise strength  γ")
plt.ylabel("Key rate (bits per state)")
plt.title("GHZ vs Pairwise BB84 — dephasing, N=3")
plt.legend()
plt.grid(alpha=0.3)
plt.savefig("crossover.png", dpi=150)
plt.show()