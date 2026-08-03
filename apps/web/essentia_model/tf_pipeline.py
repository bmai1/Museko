import numpy as np
import tensorflow as tf
import librosa
 
SAMPLE_RATE = 16000
FRAME_SIZE = 512
HOP_SIZE = 256
NUM_MEL_BANDS = 96
PATCH_SIZE = 128
PATCH_HOP_SIZE = 62
 
# Precompute the mel filterbank once. This matches Essentia's
# warpingFormula='slaneyMel', normalize='unit_tri' combination.
_MEL_FILTERBANK = tf.constant(
    librosa.filters.mel(
        sr=SAMPLE_RATE,
        n_fft=FRAME_SIZE,
        n_mels=NUM_MEL_BANDS,
        fmin=0.0,
        fmax=SAMPLE_RATE / 2,
        htk=False,
        norm="slaney",
    ).T,  # (fft_bins, n_mels) so we can right-multiply
    dtype=tf.float32,
)
 
 
def load_mono_audio(file_path, target_sr=SAMPLE_RATE):
    """
    Loads an audio file, mixes to mono, and resamples to target_sr.
    Replacement for essentia.standard.MonoLoader.
 
    Returns a 1-D float32 numpy array in [-1, 1], matching what
    MonoLoader produces.
    """
    audio, _ = librosa.load(file_path, sr=target_sr, mono=True)
    return audio.astype(np.float32)
 
 
@tf.function
def compute_log_mel_spectrogram(audio):
    """
    audio: 1-D float32 tensor of samples at SAMPLE_RATE.
    Returns: (num_frames, NUM_MEL_BANDS) float32 tensor.
 
    Pipeline: Hann-windowed STFT -> power spectrum -> mel filterbank ->
    log10(1 + 10000 * x) compression, matching TensorflowInputMusiCNN.
    """
    stft = tf.signal.stft(
        audio,
        frame_length=FRAME_SIZE,
        frame_step=HOP_SIZE,
        fft_length=FRAME_SIZE,
        window_fn=tf.signal.hann_window,
        pad_end=False,
    )
    power_spectrum = tf.square(tf.abs(stft))
    mel_spectrogram = tf.matmul(power_spectrum, _MEL_FILTERBANK)
    mel_spectrogram = tf.maximum(mel_spectrogram, 0.0)
 
    # Essentia UnaryOperator(shift=1, scale=10000) followed by log10.
    log_mel = tf.math.log(1.0 + 10000.0 * mel_spectrogram) / tf.math.log(10.0)
    return log_mel
 
 
def patchify(log_mel, patch_size=PATCH_SIZE, patch_hop=PATCH_HOP_SIZE):
    """
    Slices a (num_frames, n_mels) mel-spectrogram into overlapping patches
    of shape (patch_size, n_mels), matching lastPatchMode='discard'.
 
    Returns a float32 tensor of shape (num_patches, 1, patch_size, n_mels),
    i.e. already shaped for the model's (batch, 1, patchSize, numberBands)
    input signature.
    """
    log_mel = np.asarray(log_mel)
    num_frames = log_mel.shape[0]
 
    if num_frames < patch_size:
        # Not enough audio for a single patch; zero-pad once like Essentia's
        # 'same'/'repeat' handling of short inputs.
        pad = patch_size - num_frames
        log_mel = np.pad(log_mel, ((0, pad), (0, 0)), mode="constant")
        num_frames = log_mel.shape[0]
 
    starts = range(0, num_frames - patch_size + 1, patch_hop)
    patches = np.stack([log_mel[s:s + patch_size] for s in starts], axis=0)
    patches = patches[:, np.newaxis, :, :]  # (num_patches, 1, patch_size, n_mels)
    return patches.astype(np.float32)
 
 
def extract_patches_from_file(file_path):
    """
    Convenience end-to-end helper: file path -> patched tensor ready to feed
    to the effnet-discogs frozen graph.
    """
    audio = load_mono_audio(file_path)
    log_mel = compute_log_mel_spectrogram(tf.constant(audio)).numpy()
    return patchify(log_mel)