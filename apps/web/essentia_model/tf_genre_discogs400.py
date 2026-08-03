import io
import os
 
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
 
from .genre_data import genre_names
from .tf_pipeline import extract_patches_from_file
 
# Node names as published in the essentia model-zoo metadata for these
# specific graphs (see the .json sidecar files that ship with the .pb files).
EFFNET_INPUT_NODE = "serving_default_melspectrogram:0"
EFFNET_OUTPUT_NODE = "PartitionedCall:1"
GENRE_INPUT_NODE = "serving_default_model_Placeholder:0"
GENRE_OUTPUT_NODE = "PartitionedCall:0"
 
_GRAPH_CACHE = {}
 
 
def _wrap_frozen_graph(graph_def, inputs, outputs):
    """Standard TF2 recipe for turning a frozen GraphDef into a callable."""
    def _imports_graph_def():
        tf.compat.v1.import_graph_def(graph_def, name="")
 
    wrapped_import = tf.compat.v1.wrap_function(_imports_graph_def, [])
    graph = wrapped_import.graph
    return wrapped_import.prune(
        tf.nest.map_structure(graph.as_graph_element, inputs),
        tf.nest.map_structure(graph.as_graph_element, outputs),
    )
 
 
def _load_frozen_graph_fn(pb_path, input_node, output_node):
    """Loads and caches a callable for a frozen .pb graph file."""
    cache_key = (pb_path, input_node, output_node)
    if cache_key in _GRAPH_CACHE:
        return _GRAPH_CACHE[cache_key]
 
    with tf.io.gfile.GFile(pb_path, "rb") as f:
        graph_def = tf.compat.v1.GraphDef()
        graph_def.ParseFromString(f.read())
 
    fn = _wrap_frozen_graph(graph_def, inputs=input_node, outputs=output_node)
    _GRAPH_CACHE[cache_key] = fn
    return fn
 
 
def classify(filename):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    effnet_model_path = os.path.join(base_dir, "discogs-effnet-bs64-1.pb")
    genre_model_path = os.path.join(base_dir, "genre_discogs400-discogs-effnet-1.pb")
 
    if not os.path.exists(effnet_model_path):
        raise FileNotFoundError(f"Effnet model file not found at {effnet_model_path}")
    if not os.path.exists(genre_model_path):
        raise FileNotFoundError(f"Genre model file not found at {genre_model_path}")
 
    # --- Preprocessing (replaces MonoLoader + internal TensorflowInputMusiCNN) ---
    patches = extract_patches_from_file(filename)  # (num_patches, 1, 128, 96)
 
    # --- Embeddings (replaces TensorflowPredictEffnetDiscogs) ---
    effnet_fn = _load_frozen_graph_fn(effnet_model_path, EFFNET_INPUT_NODE, EFFNET_OUTPUT_NODE)
    embeddings = effnet_fn(tf.constant(patches)).numpy()
 
    # --- Genre prediction (replaces TensorflowPredict2D) ---
    genre_fn = _load_frozen_graph_fn(genre_model_path, GENRE_INPUT_NODE, GENRE_OUTPUT_NODE)
    predictions = genre_fn(tf.constant(embeddings)).numpy()
 
    average_predictions = np.mean(predictions, axis=0)
    if average_predictions.ndim > 1:
        average_predictions = average_predictions.squeeze()
 
    sorted_indices = np.argsort(average_predictions)[::-1]
    sorted_genres = [genre_names[i] for i in sorted_indices]
    sorted_predictions = average_predictions[sorted_indices]
 
    top_n = 10
    top_genres = sorted_genres[:top_n]
    top_scores = sorted_predictions[:top_n]
 
    plt.switch_backend("Agg")
    plt.figure(figsize=(6, 6))
    plt.bar(top_genres, top_scores, color="skyblue")
    plt.xlabel("Genres")
    plt.ylabel("Confidence Level")
    plt.title(f"Top {top_n} Predicted Genres")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
 
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()
 
    return buffer