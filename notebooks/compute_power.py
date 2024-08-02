import pywt
import numpy as np

def compute_freq_band_power(X, sfreq):
    """ Computes the power for EEG frequnecy bands

    Parameters:
    X (nd.array) : EEG data of shape (n_trials, n_channels, n_samples)
    sfreq (int) : Sampling frequency of electrodes

    Returns:
    band_power (dict) : Computed power for EEG frequency bands
    
    """
    bands = {
        'Delta': (0.5, 4),
        'Theta': (4, 8),
        'Alpha': (8, 13),
        'Beta': (13, 30),
        'Gamma': (30, 70),
        'High Gamma': (70, 150)
    }
    
    band_power = {freq_band: [] for freq_band in bands.keys()}

    for band, (low_freq, high_freq) in bands.items():
        for trial_data in X:
            coefficients, freqs = wavelet_transform(trial_data, sfreq)

            # Find the indices of frequencies within the band
            idx_band = np.logical_and(freqs >= low_freq, freqs <= high_freq)
            band_power[band].append(coefficients[idx_band, :, :].mean(axis=0))

    return band_power

def wavelet_transform(eeg_signal, fs):

    # Define wavelet parameters
    wavelet = 'cmor1.5-1.0'  # Complex Morlet wavelet
    scales = np.arange(1, 128)
    
    # Perform Continuous Wavelet Transform (CWT)
    coefficients, frequencies = pywt.cwt(eeg_signal, scales, wavelet, sampling_period=1/fs)
    
    return coefficients, frequencies