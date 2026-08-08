"""
Sharpe fitness + Harris Hawks Optimization loop.
Direct port of notebook cells 18-19.
"""
import numpy as np
from quantum_layer import quantum_levy_step

RISK_FREE = 0.02


def sharpe_fitness(w, mu, Sigma):
    w = np.clip(w, 0, None)
    if w.sum() == 0:
        return -999
    w = w / w.sum()
    ret = w @ mu
    vol = np.sqrt(w @ Sigma @ w)
    return -999 if vol == 0 else (ret - RISK_FREE) / vol


def run_hho(mu, Sigma, UB, dim, pop_size=25, max_iter=40, use_quantum=True):
    X = np.random.rand(pop_size, dim)
    X = X / X.sum(axis=1, keepdims=True)

    best, best_fit = X[0].copy(), -999

    for t in range(max_iter):
        E0 = np.random.uniform(-1, 1)
        E = 2 * E0 * (1 - t / max_iter)
        mean_pos = X.mean(axis=0)

        for i in range(pop_size):
            q = np.random.rand()
            if abs(E) >= 1:  # Exploration
                if q < 0.5:
                    X[i] = np.random.rand(dim)
                else:
                    X[i] = mean_pos - np.random.rand() * abs(mean_pos - X[i])
            else:  # Exploitation
                r = np.random.rand()
                step = quantum_levy_step(dim) if use_quantum else np.random.uniform(-0.01, 0.01, dim)
                if abs(E) >= 0.5 and r >= 0.5:  # Soft besiege
                    X[i] = best - E * abs(best - X[i])
                elif abs(E) < 0.5 and r >= 0.5:  # Hard besiege
                    X[i] = best - E * abs(best - mean_pos)
                elif abs(E) >= 0.5 and r < 0.5:  # Soft + Levy
                    X[i] = best - E * abs(best - X[i]) + step
                else:  # Hard + Levy
                    X[i] = best - E * abs(best - mean_pos) + step

            X[i] = np.clip(X[i], 0, UB)  # sentiment guardrail
            if X[i].sum() > 0:
                X[i] = X[i] / X[i].sum()

            fit = sharpe_fitness(X[i], mu, Sigma)
            if fit > best_fit:
                best_fit, best = fit, X[i].copy()

    return best, best_fit
