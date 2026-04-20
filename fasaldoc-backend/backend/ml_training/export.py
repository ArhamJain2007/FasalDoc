"""
Export trained Keras model to INT8-quantized TFLite.
Entry point for ml_training/export.py.
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.ml.tflite_exporter import export_tflite

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export Keras model to INT8 TFLite")
    parser.add_argument(
        "--model",
        default="models/plant_disease_efficientnet.keras",
        help="Path to trained .keras model",
    )
    parser.add_argument(
        "--output",
        default="models/plant_disease.tflite",
        help="Output TFLite file path",
    )
    parser.add_argument(
        "--images",
        default="data/plantvillage/*/*.jpg",
        help="Glob pattern for calibration images",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=100,
        help="Number of calibration samples for INT8 quantization",
    )
    args = parser.parse_args()

    export_tflite(
        model_path=args.model,
        output_path=args.output,
        representative_images_glob=args.images,
        num_calibration_samples=args.samples,
    )
