import cirq
import numpy as np

Z_BASIS, X_BASIS = 0, 1


def build_circuit(alice_bit, alice_basis, bob_basis):
    qubit = cirq.NamedQubit("q0")
    circuit = cirq.Circuit()

    if alice_bit == 1:
        circuit.append(cirq.X(qubit))

    if alice_basis == X_BASIS:
        circuit.append(cirq.H(qubit))

    if bob_basis == X_BASIS:
        circuit.append(cirq.H(qubit))

    
    circuit.append(cirq.measure(qubit, key='bob'))

    return circuit


def run_bb84(n_qubits = 500, seed = None):
    rng = np.random.default_rng(seed)
    simulator = cirq.Simulator(seed=seed)

    alice_bits = rng.integers(0, 2, n_qubits)
    alice_bases = rng.integers(0, 2, n_qubits)
    bob_bases = rng.integers(0, 2, n_qubits)

    bob_bits = np.zeros(n_qubits, dtype=int)

    for i in range(n_qubits):
        circuit = build_circuit(alice_bits[i], alice_bases[i], bob_bases[i])
        result = simulator.run(circuit, repetitions=1)
        bob_bits[i] = result.measurements['bob'][0][0]
    return {
        
        'alice_bits': alice_bits,
        'alice_bases': alice_bases,
        'bob_bases': bob_bases,
        'bob_bits': bob_bits
    }

def sift(alice_bits, alice_bases, bob_bases, bob_bits):
    match = alice_bases == bob_bases
    return alice_bits[match], bob_bits[match]

if __name__ == "__main__":
    data = run_bb84(n_qubits=500, seed=42)

    a_sift, b_sift = sift(data["alice_bits"], data["alice_bases"],
                          data["bob_bases"], data["bob_bits"])

    n = len(data["alice_bits"])
    print(f"sifted {len(a_sift)} of {n} ({len(a_sift)/n:.1%})")
    print("identical:", np.array_equal(a_sift, b_sift))

    mm = data["alice_bases"] != data["bob_bases"]
    print(f"agreement where bases differed: {np.mean(data['alice_bits'][mm] == data['bob_bits'][mm]):.1%}")
    print("\nfirst 20 sifted bits:", a_sift[:20])