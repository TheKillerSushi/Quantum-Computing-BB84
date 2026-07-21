import cirq
import numpy as np

Z_BASIS, X_BASIS = 0, 1

class BB84:
    def __init__(self):
        self.qubit = cirq.NamedQubit("q0")
        self.simulator = cirq.Simulator()
        self.build_alice_circuits()
        self.build_bob_circuits()

    def build_alice_circuits(self):
        q = self.qubit
        self.alice_send_0_no_H = cirq.Circuit([cirq.I(q), cirq.I(q)])
        self.alice_send_1_no_H = cirq.Circuit([cirq.X(q), cirq.I(q)])
        self.alice_send_0_H    = cirq.Circuit([cirq.I(q), cirq.H(q)])
        self.alice_send_1_H    = cirq.Circuit([cirq.X(q), cirq.H(q)])


    def build_bob_circuits(self):
        q = self.qubit
        self.bob_recieve_no_H_circuit = cirq.Circuit([cirq.I(q), cirq.measure(q, key='bob')])
        self.bob_recieve_H_circuit = cirq.Circuit([cirq.H(q), cirq.measure(q, key='bob')])
    
    def alice_circuit(self, bit, basis):
        if basis == Z_BASIS:
            return self.alice_send_0_no_H if bit == 0 else self.alice_send_1_no_H
        return self.alice_send_0_H if bit == 0 else self.alice_send_1_H
    
    def bob_circuit(self, basis):
        return self.bob_recieve_H_circuit if basis == X_BASIS else self.bob_recieve_no_H_circuit
    
    def one_round(self, alice_bit, alice_basis, bob_basis):
        sent = self.simulator.simulate(self.alice_circuit(alice_bit, alice_basis)).final_state_vector
        recieved = self.simulator.simulate(self.bob_circuit(bob_basis), initial_state=sent)
        return int(recieved.measurements['bob'][0])
    
def run_bb84(n_qubits = 500, seed = None):
    rng = np.random.default_rng(seed)
    protocol = BB84()

    protocol.simulator = cirq.Simulator(seed=seed)


    alice_bits = rng.integers(0, 2, n_qubits)
    alice_bases = rng.integers(0, 2, n_qubits)
    bob_bases = rng.integers(0, 2, n_qubits)

    bob_bits = np.zeros(n_qubits, dtype=int)

    for i in range(n_qubits):
        bob_bits[i] = protocol.one_round(alice_bits[i], alice_bases[i], bob_bases[i])
    
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





