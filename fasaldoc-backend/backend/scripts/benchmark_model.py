"""
Benchmark script: measures inference latency and throughput for both
Keras and TFLite model backends.

Usage:
  python scripts/benchmark_model.py --model models/plant_disease_efficientnet.keras
  python scripts/benchmark_model.py --tflite models/plant_disease.tflite
"""
import argparse
import io
import os
import sys
import time
import statistics

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def make_dummy_image(size: int = 224) -> bytes:
    """Generate a synthetic leaf-colored image for benchmarking."""
    img = Image.new("RGB", (size, size), color=(34, 139, 34))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def benchmark_keras(model_path: str, n_runs: int = 100, warmup: int = 10) -> dict:
    """
    Benchmark Keras model inference latency.

    Args:
        model_path: Path to .keras or SavedModel.
        n_runs: Number of timed inference runs.
        warmup: Number of warmup runs (not timed).
    Returns:
        Dict with p50, p95, p99, mean latency in ms and throughput in req/s.
    """
    import tensorflow as tf
    from app.ml.preprocessing import preprocess_bytes

    print(f"Loading Keras model from {model_path}...")
    model = tf.keras.models.load_model(model_path)
    image_bytes = make_dummy_image()
    tensor = preprocess_bytes(image_bytes)

    print(f"Warming up ({warmup} runs)...")
    for _ in range(warmup):
        model.predict(tensor, verbose=0)

    print(f"Benchmarking ({n_runs} runs)...")
    latencies = []
    for i in range(n_runs):
        start = time.perf_counter()
        model.predict(tensor, verbose=0)
        elapsed_ms = (time.perf_counter() - start) * 1000
        latencies.append(elapsed_ms)
        if (i + 1) % 20 == 0:
            print(f"  {i+1}/{n_runs} runs complete")

    return _compute_stats(latencies, "Keras")


def benchmark_tflite(tflite_path: str, n_runs: int = 100, warmup: int = 10) -> dict:
    """
    Benchmark TFLite interpreter inference latency.

    Args:
        tflite_path: Path to .tflite file.
        n_runs: Number of timed inference runs.
        warmup: Number of warmup runs (not timed).
    Returns:
        Dict with p50, p95, p99, mean latency in ms and throughput in req/s.
    """
    import tensorflow as tf
    from app.ml.preprocessing import preprocess_bytes

    print(f"Loading TFLite model from {tflite_path}...")
    interpreter = tf.lite.Interpreter(tflite_path)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    image_bytes = make_dummy_image()
    tensor = preprocess_bytes(image_bytes)

    # Handle INT8 quantization
    input_dtype = input_details[0]["dtype"]
    if input_dtype == np.int8:
        scale, zero_point = input_details[0]["quantization"]
        input_tensor = (tensor / scale + zero_point).astype(np.int8)
    else:
        input_tensor = tensor

    print(f"Warming up ({warmup} runs)...")
    for _ in range(warmup):
        interpreter.set_tensor(input_details[0]["index"], input_tensor)
        interpreter.invoke()

    print(f"Benchmarking ({n_runs} runs)...")
    latencies = []
    for i in range(n_runs):
        start = time.perf_counter()
        interpreter.set_tensor(input_details[0]["index"], input_tensor)
        interpreter.invoke()
        _ = interpreter.get_tensor(output_details[0]["index"])
        elapsed_ms = (time.perf_counter() - start) * 1000
        latencies.append(elapsed_ms)
        if (i + 1) % 20 == 0:
            print(f"  {i+1}/{n_runs} runs complete")

    return _compute_stats(latencies, "TFLite")


def _compute_stats(latencies: list[float], backend: str) -> dict:
    sorted_lat = sorted(latencies)
    n = len(sorted_lat)
    stats = {
        "backend": backend,
        "n_runs": n,
        "mean_ms": round(statistics.mean(latencies), 2),
        "median_ms": round(statistics.median(latencies), 2),
        "p95_ms": round(sorted_lat[int(n * 0.95)], 2),
        "p99_ms": round(sorted_lat[int(n * 0.99)], 2),
        "min_ms": round(min(latencies), 2),
        "max_ms": round(max(latencies), 2),
        "throughput_rps": round(1000 / statistics.mean(latencies), 1),
    }

    print(f"\n{'='*50}")
    print(f"  {backend} Benchmark Results")
    print(f"{'='*50}")
    print(f"  Runs:         {stats['n_runs']}")
    print(f"  Mean:         {stats['mean_ms']} ms")
    print(f"  Median (p50): {stats['median_ms']} ms")
    print(f"  p95:          {stats['p95_ms']} ms")
    print(f"  p99:          {stats['p99_ms']} ms")
    print(f"  Min:          {stats['min_ms']} ms")
    print(f"  Max:          {stats['max_ms']} ms")
    print(f"  Throughput:   {stats['throughput_rps']} req/s")
    print(f"{'='*50}\n")

    # Performance targets check
    target_p95 = 800 if backend == "Keras" else 150
    status = "✓ PASS" if stats["p95_ms"] < target_p95 else "✗ FAIL"
    print(f"  Target p95 < {target_p95} ms: {status} ({stats['p95_ms']} ms)")

    return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark FasalDoc ML model inference")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--model", help="Path to Keras .keras model")
    group.add_argument("--tflite", help="Path to TFLite .tflite model")
    parser.add_argument("--runs", type=int, default=100, help="Number of benchmark runs")
    parser.add_argument("--warmup", type=int, default=10, help="Number of warmup runs")
    args = parser.parse_args()

    if args.model:
        benchmark_keras(args.model, n_runs=args.runs, warmup=args.warmup)
    else:
        benchmark_tflite(args.tflite, n_runs=args.runs, warmup=args.warmup)
