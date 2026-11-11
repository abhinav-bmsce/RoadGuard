"""
RoadGuard - Inference Latency & FPS Benchmark
Benchmarks model forward pass and post-processing latency across CPU, MPS (Apple Silicon), and CUDA.
"""

import time
import argparse
import numpy as np
import torch
from ultralytics import YOLO


def benchmark_latency(weights_path: str, device: str = "cpu", iterations: int = 100, imgsz: int = 640):
    print("=" * 60)
    print(" RoadGuard - Latency & Throughput Benchmark")
    print(f"Model: {weights_path} | Device: {device} | Iterations: {iterations} | Resolution: {imgsz}x{imgsz}")
    print("=" * 60)

    # Determine device
    if device == "mps" and not torch.backends.mps.is_available():
        print("Warning: Apple MPS not available, falling back to CPU")
        device = "cpu"
    elif device == "cuda" and not torch.cuda.is_available():
        print("Warning: CUDA not available, falling back to CPU")
        device = "cpu"

    model = YOLO(weights_path)
    
    # Create dummy road frame
    dummy_input = np.random.randint(0, 255, (imgsz, imgsz, 3), dtype=np.uint8)

    # Warmup runs
    print("Warming up engine (10 iterations)...")
    for _ in range(10):
        _ = model.predict(dummy_input, device=device, verbose=False)

    latencies = []
    print(f"Running {iterations} benchmark inference passes...")
    for _ in range(iterations):
        t0 = time.perf_counter()
        _ = model.predict(dummy_input, device=device, verbose=False)
        t1 = time.perf_counter()
        latencies.append((t1 - t0) * 1000.0)  # ms

    latencies = np.array(latencies)
    mean_lat = np.mean(latencies)
    std_lat = np.std(latencies)
    p50 = np.percentile(latencies, 50)
    p95 = np.percentile(latencies, 95)
    fps = 1000.0 / mean_lat

    print("\n--- Latency Benchmark Results ---")
    print(f"Mean Latency : {mean_lat:.2f} ms (+/- {std_lat:.2f} ms)")
    print(f"Median (P50) : {p50:.2f} ms")
    print(f"95th %ile    : {p95:.2f} ms")
    print(f"Throughput   : {fps:.1f} Frames Per Second (FPS)")
    print(f"Real-Time OK : {'YES (>24 FPS)' if fps >= 24 else 'Marginal / Non-realtime'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark Inference Latency")
    parser.add_argument("--weights", type=str, default="ml/models/roadguard_yolov8n.pt")
    parser.add_argument("--device", type=str, default="cpu", choices=["cpu", "mps", "cuda"])
    parser.add_argument("--iterations", type=int, default=50)
    parser.add_argument("--imgsz", type=int, default=640)
    args = parser.parse_args()

    benchmark_latency(args.weights, args.device, args.iterations, args.imgsz)

