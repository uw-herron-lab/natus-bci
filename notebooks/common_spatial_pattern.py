import numpy as np
from scipy.linalg import eigh

def compute_covariance_matrix(data):
    """Compute the covariance matrix for EEG data.
    
    Parameters:
    data (ndarray): EEG data of shape (n_channels, n_samples)
    
    Returns:
    ndarray: Covariance matrix of shape (n_channels, n_channels)
    """
    # Subtract the mean for each channel
    data = data - np.mean(data, axis=1, keepdims=True)
    # Compute covariance matrix
    cov_matrix = np.dot(data, data.T) / data.shape[1]
    return cov_matrix

def csp(X1, X2):
    """Compute the Common Spatial Patterns (CSP) filters.
    
    Parameters:
    X1 (ndarray): EEG data for class 1, shape (n_trials, n_channels, n_samples)
    X2 (ndarray): EEG data for class 2, shape (n_trials, n_channels, n_samples)
    
    Returns:
    ndarray: CSP filters of shape (n_channels, n_channels)
    """
    # Compute average covariance matrices for each class
    cov1 = np.mean([compute_covariance_matrix(trial) for trial in X1], axis=0)
    cov2 = np.mean([compute_covariance_matrix(trial) for trial in X2], axis=0)
    
    # Composite covariance matrix
    cov_total = cov1 + cov2
    
    # Solve the generalized eigenvalue problem
    eigenvalues, eigenvectors = eigh(cov1, cov_total)
    
    # Sort eigenvalues and corresponding eigenvectors in descending order
    sorted_indices = np.argsort(eigenvalues)[::-1]
    eigenvectors = eigenvectors[:, sorted_indices]
    
    return eigenvectors