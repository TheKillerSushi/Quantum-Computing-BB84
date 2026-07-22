import cirq
import numpy as np
from numpy.random import gamma
import matplotlib.pyplot as plt
import csv

SIM = cirq.DensityMatrixSimulator(dtype = np.complex128)

''' Binary Shannon Entropy Function'''

def h(x):
    x = np.clip(x, 0.0, 1.0)
    if x <= 0.0 or x >= 1.0:
        return 0.0
    return -x * np.log2(x) - (1.0 - x) * np.log2(1.0 - x)

def analytic_crossover(N):
    '''Find dephasing crossover analytically for N qubits'''
    for lam in np.linspace(0, 0.9, 9001):
        qx_ghz = (1 -  (1 - lam) ** (N/2)) / 2
        r_ghz = max(0, 1-h(qx_ghz))

        qx_bell = lam / 2
        r_pair = max(0.0, 1 - h(qx_bell)) / (N-1)

        if r_ghz < r_pair:
            return lam
    return None

def ghz_circuit(n, noise=None, gamma=None):
    '''Builds an n-qubit GHZ state, now with noise'''
    q = cirq.LineQubit.range(n)
    c = cirq.Circuit()
    c.append(cirq.H(q[0]))
    for i in range(1, n):
        c.append(cirq.CNOT(q[0], q[i]))

    if noise is not None:
        channel = {
            "amplitude": cirq.amplitude_damp,
            "phase": cirq.phase_damp,
            "depolarize": cirq.depolarize,
        } [noise](gamma)
        c.append(channel.on_each(*q))
    return q, c

def get_expectations(q, c):
    ## Measure <XXX> and each <Z0 Zi> on the circuit
    x_all = cirq.PauliString({qubit: cirq.X for qubit in q})
    z_pairs = [cirq.PauliString({q[0]: cirq.Z, q[i]: cirq.Z}) 
               for i in range(1, len(q))]
    results = SIM.simulate_expectation_values(c, observables=[x_all] + z_pairs)
    results = [float(np.real(v)) for v in results]
    return results[0], results[1:]


def qbers(q, c):
    """Convert expectation values into error rates Q_X/<Q_Z>"""
    parity, pairs = get_expectations(q, c)
    q_x = (1.0 - parity) / 2.0
    q_z_list = [(1.0 - p) / 2.0 for p in pairs]
    return q_x, q_z_list

def ghz_key_rate(n, noise=None, gamma=0.0):
    q, c = ghz_circuit(n, noise, gamma)
    q_x, q_z_list = qbers(q, c)
    rate = 1 - h(q_x) - max([h(q_z) for q_z in q_z_list])
    return max(0.0, rate)

def bell_circuit(noise=None, gamma=0.0):
    '''Builds a 2-qubit Bell state, now with noise'''
    q = cirq.LineQubit.range(2)
    c = cirq.Circuit()
    c.append(cirq.H(q[0]))
    c.append(cirq.CNOT(q[0], q[1]))

    if noise is not None:
        channel = {
            "amplitude": cirq.amplitude_damp,
            "phase": cirq.phase_damp,
            "depolarize": cirq.depolarize,
        } [noise](gamma)
        c.append(channel.on_each(*q))
    return q, c

def pairwise_key_rate(n, noise=None, gamma=0.0):
    '''Conference key rate if Alice runs BB84 with each Bob separately'''
    q, c = bell_circuit(noise, gamma)
    q_x, q_z_list = qbers(q, c)
    rate = 1 - h(q_x) - max([h(q_z) for q_z in q_z_list])
    return max(0.0, rate) / (n - 1)


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

noise_types = ["phase", "amplitude", "depolarize"]
group_sizes = [3, 4, 5]

print(f"{'Noise':<12}{'N':<4}{'Crossover': <12}{'GHZ dies':<10}")
print("-" * 38)

for noise in noise_types:
    for n in group_sizes:
        ghz_rates = [ghz_key_rate(n, noise, g) for g in gammas]
        pw_rates = [pairwise_key_rate(n, noise, g) for g in gammas]

        crossover = None
        for i in range(len(gammas)):
            if ghz_rates[i] < pw_rates[i]:
                crossover = gammas[i]
                break
        
        ghz_dies = None
        for i in range(len(gammas)):
            if ghz_rates[i] <= 1e-9:
                ghz_dies = gammas[i]
                break
        
        cx = f"{crossover:.3f}" if crossover is not None else "--"
        dz = f"{ghz_dies:.3f}" if ghz_dies is not None else "--"
        print(f"{noise:<12}{n:<4}{cx:<12}{dz:<10}")
    print()

with open("results.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["noise", "N", "crossover", "ghz_dies"])

    for noise in noise_types:
        for n in group_sizes:
            ghz_rates = [ghz_key_rate(n, noise, g) for g in gammas]
            pw_rates = [pairwise_key_rate(n, noise, g) for g in gammas]

            crossover = None
            for i in range(len(gammas)):
                if ghz_rates[i] < pw_rates[i]:
                    crossover = round(gammas[i], 3)
                    break

            ghz_dies = None
            for i in range(len(gammas)):
                if ghz_rates[i] <= 1e-9:
                    ghz_dies = round(gammas[i], 3)
                    break

            writer.writerow([noise, n, crossover, ghz_dies])

print("Saved results.csv")
for N in [3, 4, 5]:
    print(f"N={N}: analytic crossover = {analytic_crossover(N):.3f}")

Ns = [3, 4, 5]

analytic = [analytic_crossover(N) for N in Ns]

simulated = [0.488, 0.410, 0.357]

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