"""
TFLite model export utility.
Converts a trained Keras model to an INT8-quantized TFLite model.
Target: <15MB, <100ms inference on mid-range Android.
"""
import os
import glob
import numpy as np
import tensorflow as tf
from PIL import Image

from app.ml.preprocessing import preprocess_image


def export_tflite(
    model_path: str,
    output_path: str,
    representative_images_glob: str = "data/plantvillage/*/*.jpg",
    num_calibration_samples: int = 100,
) -> None:
    """
    Convert a Keras SavedModel to INT8-quantized TFLite.

    Args:
        model_path: Path to .keras or SavedModel directory.
        output_path: Destination .tflite file path.
        representative_images_glob: Glob pattern for calibration images.
        num_calibration_samples: Number of images used for INT8 calibration.
    Side effects:
        Writes .tflite file to output_path.
        Prints model size summary to stdout.
    """
    model = tf.keras.models.load_model(model_path)
    converter = tf.lite.TFLiteConverter.from_keras_model(model)

    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.target_spec.supported_ops = [
        tf.lite.OpsSet.TFLITE_BUILTINS_INT8
    ]

    # Gather calibration image paths
    sample_image_paths = sorted(glob.glob(representative_images_glob))[:num_calibration_samples]
    if len(sample_image_paths) < num_calibration_samples:
        print(
            f"Warning: only {len(sample_image_paths)} calibration images found "
            f"(requested {num_calibration_samples}). Quantization quality may be reduced."
        )

    def representative_data_gen():
        for img_path in sample_image_paths:
            try:
                img = Image.open(img_path).convert("RGB")
                tensor = preprocess_image(img)
                yield [tensor]
            except Exception as exc:
                print(f"Skipping {img_path}: {exc}")
                continue

    converter.representative_dataset = representative_data_gen
    converter.inference_input_type = tf.int8
    converter.inference_output_type = tf.int8

    tflite_model = converter.convert()

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(tflite_model)

    size_mb = len(tflite_model) / 1024 / 1024
    print(f"✓ TFLite model saved: {size_mb:.1f} MB → {output_path}")
    if size_mb > 15:
        print(f"⚠ Model size {size_mb:.1f} MB exceeds 15 MB target.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Export Keras model to INT8 TFLite")
    parser.add_argument("--model", default="models/plant_disease_efficientnet.keras")
    parser.add_argument("--output", default="models/plant_disease.tflite")
    parser.add_argument("--images", default="data/plantvillage/*/*.jpg")
    parser.add_argument("--samples", type=int, default=100)
    args = parser.parse_args()

    export_tflite(args.model, args.output, args.images, args.samples)
