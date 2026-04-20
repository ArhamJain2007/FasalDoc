"""
Model evaluation: accuracy, per-class metrics, and confusion matrix.
"""
import argparse
import os
import numpy as np
import tensorflow as tf
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    top_k_accuracy_score,
)

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.ml.classes import PLANT_DISEASE_CLASSES
from ml_training.dataset import build_datasets


def evaluate(
    model_path: str,
    data_dir: str,
    batch_size: int = 32,
    input_size: int = 224,
    output_dir: str = "eval_results",
) -> dict:
    """
    Evaluate model on the validation set.
    Outputs accuracy, per-class F1, and saves confusion matrix PNG.

    Args:
        model_path: Path to .keras or SavedModel.
        data_dir: PlantVillage root directory.
        batch_size: Evaluation batch size.
        input_size: Image size used during training.
        output_dir: Directory for saving evaluation artifacts.
    Returns:
        Dict with top1_accuracy, top3_accuracy, and per_class_metrics.
    """
    os.makedirs(output_dir, exist_ok=True)

    print(f"Loading model from {model_path}...")
    model = tf.keras.models.load_model(model_path)

    _, val_ds = build_datasets(
        data_dir=data_dir,
        input_size=input_size,
        batch_size=batch_size,
    )

    print("Running inference on validation set...")
    all_preds = []
    all_labels = []

    for images, labels in val_ds:
        preds = model.predict(images, verbose=0)
        all_preds.append(preds)
        all_labels.append(labels.numpy())

    all_preds = np.concatenate(all_preds, axis=0)
    all_labels = np.concatenate(all_labels, axis=0)

    y_true = np.argmax(all_labels, axis=1)
    y_pred = np.argmax(all_preds, axis=1)

    # Top-1 accuracy
    top1 = float(np.mean(y_true == y_pred))
    print(f"\nTop-1 Accuracy: {top1:.4f} ({top1*100:.2f}%)")

    # Top-3 accuracy
    top3 = top_k_accuracy_score(y_true, all_preds, k=3)
    print(f"Top-3 Accuracy: {top3:.4f} ({top3*100:.2f}%)")

    # Classification report
    target_names = PLANT_DISEASE_CLASSES[:len(set(y_true))]
    report = classification_report(y_true, y_pred, target_names=target_names, digits=4)
    print("\nClassification Report:")
    print(report)

    report_path = os.path.join(output_dir, "classification_report.txt")
    with open(report_path, "w") as f:
        f.write(f"Top-1 Accuracy: {top1:.4f}\n")
        f.write(f"Top-3 Accuracy: {top3:.4f}\n\n")
        f.write(report)
    print(f"Report saved to {report_path}")

    # Confusion matrix (save as CSV for large number of classes)
    cm = confusion_matrix(y_true, y_pred)
    cm_path = os.path.join(output_dir, "confusion_matrix.csv")
    np.savetxt(cm_path, cm, delimiter=",", fmt="%d")
    print(f"Confusion matrix saved to {cm_path}")

    # Per-class accuracy
    per_class = {}
    for idx, cls_name in enumerate(PLANT_DISEASE_CLASSES):
        mask = y_true == idx
        if mask.sum() > 0:
            cls_acc = float(np.mean(y_pred[mask] == idx))
            per_class[cls_name] = round(cls_acc, 4)

    # Print worst-performing classes
    sorted_classes = sorted(per_class.items(), key=lambda x: x[1])
    print("\nWorst 5 classes:")
    for name, acc in sorted_classes[:5]:
        print(f"  {name}: {acc*100:.1f}%")

    print("\nBest 5 classes:")
    for name, acc in sorted_classes[-5:]:
        print(f"  {name}: {acc*100:.1f}%")

    return {
        "top1_accuracy": top1,
        "top3_accuracy": top3,
        "per_class_metrics": per_class,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate FasalDoc plant disease model")
    parser.add_argument("--model", required=True, help="Path to .keras model")
    parser.add_argument("--data-dir", required=True, help="PlantVillage dataset root")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--output-dir", default="eval_results")
    args = parser.parse_args()

    results = evaluate(
        model_path=args.model,
        data_dir=args.data_dir,
        batch_size=args.batch_size,
        output_dir=args.output_dir,
    )
    print(f"\nFinal: Top-1={results['top1_accuracy']:.4f}, Top-3={results['top3_accuracy']:.4f}")
