from GHZ_CKA import *
import numpy as np
import csv

gammas = np.linspace(0.0, 0.6, 121)

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