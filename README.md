# Quantum-Computing-BB84

# Noise-Induced Crossover in Multipartite Quantum Key Distribution 

Ryder Carlson, Kidus Peter, and Lochlan Fitzgerald

We are testing whether sharing one Quantum Key across three or more people at once (through GHZ) holds up better or worse than exchanging keys person to person, through pairwise BB84. The results found were that the answer changes depending on the noise levels of the connection, and how many people are recieving the key.

GHZ is more efficient then BB84, but entanglement is more fragile than BB84, and something we were wondering was whether the efficiency is worth the fragility when accounting for noise.

Both protocols were simulated (in Cirq) with realistic noise, including amplitude damping, dephasing, and depolarizing. For each one, the secret key rate was compared. (Secret key rate is how much usable secure key survives)

As the noise was increased, the protocols were compared in group sizes of 3, 4, and 5.

According to these simulations, GHZ is better in low noise as it begins at automatically double the key rate of BB84 (1.0 vs 0.5). However, as noise increases, GHZ becomes worse more quickly than BB84, and eventually has a lower key rate. Essentially, below that threshold, GHZ is better, and below, BB84.

However, adding more participants (more Bobs) makes GHZ protocol worse, and the crossover happens with lower noise with each further person. BB84 isn't affected by this because it only ever involves two people.

Finally, how the noise is distributed matters significantly. Networks with uneven links, eg. one long fiber vs two short ones, the higher rate of noise on the single branch worsens the shared keymore than spreading the total noise evenly. This is not very cleanly described in existing literature to our knowledge, and would potentially be our main novel contribution.

The results have also been verified analytically to 3 decimal places.
