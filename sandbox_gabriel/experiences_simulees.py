# %%

import time
import numpy as np
import matplotlib.pyplot as plt

# %%

# faire plus tard = vectoriser ces fonctions

r"""
Coefs de la loi conditionnelle
X_{\tau} | X_0 = x_0 ~ N(\alpha(\tau)x_0, \beta_{\tau}^2 I)
"""
def alpha(tau, eps_a):
    return 1 - tau * (1 - eps_a)

def beta2(tau, eps_b):
    return eps_b + tau * (1 - eps_b)

"""
Coefs de la forward SDE (utilisé dans la discrétisation de la reverse SDE)
"""

def a(tau, eps_a):
    """
    Calcule dlog(alpha(tau))/dtau = alpha'(tau)/alpha(tau)
    """
    return -(1 - eps_a)/alpha(tau, eps_a)

def b2(tau, eps_a, eps_b):
    """
    Calcule dbeta_tau^2/dtau - 2dlog(alpah_tau)/dtau * beta_tau^2
    """
    return 1 - eps_b - 2 * a(tau, eps_a) * beta2(tau, eps_b)

"""
Scores pour guider la reverse diffusion et amener les particules vers la 
bonne postérieure ie p(x_{k+1} | y_{1:k+1})
"""

def prior_score(X_tau, X_0, tau, eps_a, eps_b):
    r"""
    - X_tau : représente l'état de la particule au temps tau durant 
    la reverse diffusion
    - X_0 : représente l'état de la particule avant la forward diffusion ie 
    la particule issu de la prediction one step avant diffusion
    On utilise l'approximation du papier : 
    \nabla_x log p(x_{k+1,tau}|y_{1:k}) \approx \nabla_x log p(x_{k+1,tau}^i | x_{k+1|k}^i)
    car on sait que X_tau | X_0 = x_0 ~ N(alpha(tau)x_0, beta_tau^2 I)
    """
    return -(X_tau - alpha(tau, eps_a) * X_0)/beta2(tau, eps_b)

def ll_score(Y, X_tau, C, std_obs):
    """
    - X_tau : représente l'état de la particule au temps tau durant 
    la reverse diffusion
    - Y : observation courante
    - C : matrice dans l'équation d'observation du SSM 
    - std_obs : écart-type du bruit d'obs
    """
    # return C.transpose() @ ((Y - C @ X_tau)/std_obs**2)
    # version vectorisée : on stocke les particules du pseudo temps tau 
    # dans une matrice Nxd i.e. une ligne = une particule
    # rajout du type pour gérer les cas de matrice diag et éviter de stocker des 
    # matrices diag énormes
    if np.isscalar(C):
        return ((Y - X_tau * C)/std_obs**2) * C
    else:
        return ((Y - X_tau @ C.T)/std_obs**2) @ C

def score(Y, X_tau, X_0, C, std_obs, tau, eps_a, eps_b):
    """
    Score dans la reversion diffusion SDE pour guider les particules 
    vers la postérieure
    """
    return (
        prior_score(X_tau, X_0, tau, eps_a, eps_b) + 
        (1 - tau) * ll_score(Y, X_tau, C, std_obs)
    )

"""
Fonction pour la forward diffusion ie on ne fait pas la discrétisation 
mais on simule directement X_{tau=1} | X_0 = x_0 ~ N(x_0 * alpha_1, beta^2_1 I)
"""

def initialize_reverse_diffusion(X_0, eps_a, eps_b, rng):
    return X_0 * alpha(1, eps_a) + np.sqrt(beta2(1, eps_b)) * rng.standard_normal(X_0.shape)

"""
Fonction pour un step dans la reverse diffusion SDE discrétisé par Euler-Maruyama
"""

def step_reverse_diffusion(Y, X_tau, X_0, C, std_obs, tau, dtau, eps_a, eps_b, rng):
    """
    A partir du X_tau courant dans la reverse diffusion et le pas dtau
    renvoie X_{tau - dtau}
    """
    score_drift = score(Y, X_tau, X_0, C, std_obs, tau, eps_a, eps_b)
    drift = (a(tau, eps_a) * X_tau - b2(tau, eps_a, eps_b) * score_drift) * dtau
    diffusion = np.sqrt(b2(tau, eps_a, eps_b) * dtau) * rng.standard_normal(X_tau.shape)
    return X_tau - drift + diffusion

def reverse_diffusion(num_steps, Y, X_0, C, std_obs, eps_a, eps_b, rng):
    # X_{tau = 1}
    X_tau = initialize_reverse_diffusion(X_0, eps_a, eps_b, rng)
    dtau = 1/num_steps
    for i in range(num_steps):
        tau = 1 - i*dtau
        X_tau = step_reverse_diffusion(Y, X_tau, X_0, C, std_obs, tau, dtau, eps_a, eps_b, rng)
    return X_tau 

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

# %%
# générations des données synthétiques
rng_data = np.random.default_rng(2003)

phi = 0.95 # coef dans la transition de X
# (2 dans l'article, mais la dynamique explose)
d = 2500 # dimension X et Y 
T = 100 # nombre d'obs

std_state = np.sqrt(0.0125)
std_obs = np.sqrt(0.01)

X_0 = rng_data.standard_normal(d)

X = np.zeros((T,d))
Y = np.zeros((T,d))
# on considère qu'on commence à Y_1|X_1 et non Y_0|X_0
X[0] = phi*X_0 + rng_data.standard_normal(d) * std_state
Y[0] = 0.25*X[0] + rng_data.standard_normal(d) * std_obs
for i in range(1,T):
    X[i] = phi*X[i-1] + rng_data.standard_normal(d) * std_state
    Y[i] = 0.25*X[i] + rng_data.standard_normal(d) * std_obs

# %%
# EnSF
rng_ensf = np.random.default_rng(1011)
num_particles = 100
num_steps = 100
# hyperparamètres que les auteurs ont tuné sur leur exemple synthétique
eps_a = 0.96
eps_b = 0.03
C = 0.25 

start_ensf = time.perf_counter()
# On initialise les particules : 
particles_ensf = np.zeros((T, num_particles, d))

# X_{1|0}
particles_ensf[0] = phi*rng_ensf.standard_normal((num_particles, d)) + rng_ensf.standard_normal((num_particles, d)) * std_state
particles_ensf[0] = reverse_diffusion(num_steps, Y[0], particles_ensf[0], C, std_obs, eps_a, eps_b, rng_ensf)
for t in range(1,T):
    particles_ensf[t] = phi*particles_ensf[t-1] + rng_ensf.standard_normal((num_particles, d)) * std_state
    particles_ensf[t] = reverse_diffusion(num_steps, Y[t], particles_ensf[t], C, std_obs, eps_a, eps_b, rng_ensf)
end_ensf = time.perf_counter()

# %% 
# BPF
rng_pf = np.random.default_rng(101103)
start_bpf = time.perf_counter()
log_W, particles_bpf, log_ESS_hist = bpf_filer(Y, num_particles, d, rng_pf, phi, std_obs, std_state, C)
end_bpf = time.perf_counter()

# %%

X_hat_bpf = np.sum(particles_bpf * np.exp(log_W)[:, :, None], axis=1)
rmse_bpf = np.sqrt(np.mean((X_hat_bpf - X)**2, axis=1))

X_hat_ensf = particles_ensf.mean(axis=1)
rmse_ensf = np.sqrt(np.mean((X_hat_ensf - X)**2, axis=1))

# %%
"""
RMSE BPF vs ENSF et difference de compute time
"""

compute_time_ensf = end_ensf - start_ensf
compute_time_bpf = end_bpf - start_bpf
fig, ax = plt.subplots()
ax.plot(np.arange(T), rmse_ensf, label=f"ENSF : {compute_time_ensf:.2f} secs")
ax.plot(np.arange(T), rmse_bpf, label=f"BPF : {compute_time_bpf:.2f} secs")
ax.set_title(f"RMSE against T, N = {num_particles} particles")
ax.legend()
plt.show()

# %%
"""
Plot de l'ESS calculé avant rééchantillonage
"""

fig, ax = plt.subplots()
ax.plot(np.exp(log_ESS_hist))
ax.axhline(y=num_particles/2, label="Seuil de rééchantillonage $\\frac{N}{2}$", color="red")
ax.set_title("ESS calculé avant rééchantillonage")
ax.legend()
plt.show()

"""
ESS est toujours bien inférieur à N/2 donc on rééchantillone à chaque fois
"""

# %%

"""
RMSE BPF pour différents nombres de particules
"""

rmses = []
for N in [500, 1000, 2000]:
    lW, particles, _ = bpf_filer(Y, N, d, rng_pf, phi, std_obs, std_state, C)
    X_hat = np.sum(particles * np.exp(lW)[:, :, None], axis=1)
    rmses.append(np.sqrt(np.mean((X_hat - X)**2, axis=1)))

fig, ax = plt.subplots()
for i, N in enumerate([500, 1000, 2000]):
    ax.plot(np.arange(T), rmses[i], label=f"N = {num_particles}")
ax.set_title("Evolution de la RMSE pour N=500, 1000 et 2000 particules")
ax.legend()
plt.show()

# %%
