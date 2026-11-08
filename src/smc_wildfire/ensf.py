# %%

import numpy as np

# %%
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