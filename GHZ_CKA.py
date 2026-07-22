import cirq
import numpy as np
import matplotlib.pyplot as plt

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

def ghz_circuit_asym(gammas_list, noise="phase"):
    """Builds n qubit GHZ state with asymmetric noise on each qubit"""
    n = len(gammas_list)
    q = cirq.LineQubit.range(n)
    c = cirq.Circuit()
    c.append(cirq.H(q[0]))
    for i in range(1, n):
        c.append(cirq.CNOT(q[0], q[i]))

    channel_fn = {
        "amplitude": cirq.amplitude_damp,
        "phase": cirq.phase_damp,
        "depolarize": cirq.depolarize,
    } [noise]

    for i in range(n):
        if gammas_list[i] > 0:
            c.append(channel_fn(gammas_list[i]).on(q[i]))
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