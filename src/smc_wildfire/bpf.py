# %%

import numpy as np

# %%
"""
fonctions pour filters bpf (avec systematic resampling basé sur ESS)
"""

def systematic_resampling(W, rng, num_particles):

    W_cumsum = np.cumsum(W)
    W_cumsum[-1] = 1.0 # pour sécuriser le cumsum à cause des flottants
    U = np.zeros(num_particles)
    U[0] = rng.uniform(low=0.0, high=1/num_particles)
    for i in range(1,num_particles):
        U[i] = U[0] + i/num_particles
    return np.searchsorted(W_cumsum, U)


def log_ESS(log_W):
    """
    On utilise directement les log poids normalisés pour l'ESS et
    """
    max_log_W = np.max(2 * log_W)
    return - max_log_W - np.log(np.exp(2 * log_W - max_log_W).sum())


def bpf_filer(Y, num_particles, d, rng_pf, phi, std_obs, std_state, C):
    """
    Filtre bootstrap avec resampling systématique selon ESS
    """
    T = Y.shape[0]
    log_W = np.zeros((T, num_particles))
    particles = np.zeros((T, num_particles, d))
    log_ESS_hist = np.zeros(T)
    # init des particules
    particles_0 = rng_pf.standard_normal((num_particles, d))
    # pour éviter de le calculer plusieurs fois
    log_N = np.log(num_particles)

    # propagation ie X_1|X_0 
    particles[0] = phi*particles_0 + rng_pf.standard_normal((num_particles, d)) * std_state
    log_w = (-1/(2 * std_obs**2)*(Y[0] - C * particles[0])**2).sum(axis=1)
    max_log_w = np.max(log_w)
    # log sum exp avec trick du max pour éviter underflow/overflow et normalisation directement avec l'espace log
    log_W[0] = log_w - max_log_w - np.log((np.exp(log_w - max_log_w)).sum())

    log_ESS_curr = log_ESS(log_W[0])
    log_ESS_hist[0] = log_ESS_curr
    # systematic resampling si ESS <= N/2
    if log_ESS_curr <= log_N - np.log(2):
        idx_resampling = systematic_resampling(np.exp(log_W[0]), rng_pf, num_particles)
        particles[0] = particles[0][idx_resampling]
        log_W[0] = -log_N

    for t in range(1,T):

        particles[t] = phi*particles[t-1] + rng_pf.standard_normal((num_particles, d)) * std_state
        log_w = log_W[t-1] + (-1/(2 * std_obs**2) * ((Y[t] - C * particles[t])**2).sum(axis=1))
        max_log_w = np.max(log_w)
        log_W[t] = log_w - max_log_w - np.log((np.exp(log_w - max_log_w)).sum())

        log_ESS_curr = log_ESS(log_W[t])
        log_ESS_hist[t] = log_ESS_curr

        # systematic resampling si ESS <= N/2
        if log_ESS_curr <= log_N - np.log(2):
            idx_resampling = systematic_resampling(np.exp(log_W[t]), rng_pf, num_particles)
            particles[t] = particles[t][idx_resampling]
            log_W[t] = -log_N

    return log_W, particles, log_ESS_hist