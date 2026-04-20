"""
Training script for EfficientNetB4 plant disease classifier.
Two-phase: warm-up head → fine-tune top layers.
Dataset: PlantVillage (54,305 images, 38 classes).
"""
import os
import argparse
import numpy as np
import tensorflow as tf
from pathlib import Path

from augmentation import build_augmentation_pipeline
from dataset import build_datasets

# ── Model Architecture ───────────────────────────────────────────────────────


def build_model(num_classes: int = 38, input_size: int = 224) -> tf.keras.Model:
    """
    Build EfficientNetB4 with custom classification head.
    Phase 1: base frozen, head trainable.

    Args:
        num_classes: Number of output classes (38 for PlantVillage + Indian crops).
        input_size: Square input image dimension in pixels.
    Returns:
        Compiled Keras model ready for Phase 1 training.
    """
    base = tf.keras.applications.EfficientNetB4(
        include_top=False,
        weights="imagenet",
        input_shape=(input_size, input_size, 3),
    )
    base.trainable = False  # Phase 1: freeze base

    inputs = tf.keras.Input(shape=(input_size, input_size, 3))
    x = base(inputs, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Dropout(0.4)(x)
    x = tf.keras.layers.Dense(512, activation="relu")(x)
    x = tf.keras.layers.Dropout(0.3)(x)
    outputs = tf.keras.layers.Dense(num_classes, activation="softmax")(x)

    return tf.keras.Model(inputs, outputs, name="fasaldoc_efficientnetb4")


# ── Callbacks ────────────────────────────────────────────────────────────────


def build_callbacks(output_dir: str) -> list:
    """
    Build training callbacks: early stopping, model checkpoint, LR reduction.

    Args:
        output_dir: Directory to save best model checkpoints.
    Returns:
        List of Keras callback instances.
    """
    os.makedirs(output_dir, exist_ok=True)
    return [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy",
            patience=5,
            restore_best_weights=True,
            verbose=1,
        ),
        tf.keras.callbacks.ModelCheckpoint(
            filepath=os.path.join(output_dir, "best_model.keras"),
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1,
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.3,
            patience=3,
            min_lr=1e-7,
            verbose=1,
        ),
        tf.keras.callbacks.TensorBoard(
            log_dir=os.path.join(output_dir, "logs"),
            histogram_freq=1,
        ),
    ]


# ── Training ─────────────────────────────────────────────────────────────────


def train(
    data_dir: str,
    output_dir: str = "models",
    batch_size: int = 32,
    input_size: int = 224,
    num_classes: int = 38,
    phase1_epochs: int = 5,
    phase2_epochs: int = 20,
    unfreeze_last_n: int = 30,
) -> None:
    """
    Full two-phase training pipeline.

    Phase 1: Train classification head only (5 epochs, lr=1e-3).
    Phase 2: Fine-tune top 30 EfficientNet layers (20 epochs, lr=1e-5).

    Args:
        data_dir: Root of PlantVillage dataset (subdirs = class names).
        output_dir: Directory for saved models and logs.
        batch_size: Training batch size.
        input_size: Input image size (224 for EfficientNetB4).
        num_classes: Number of disease classes (38).
        phase1_epochs: Epochs for head warm-up.
        phase2_epochs: Epochs for fine-tuning.
        unfreeze_last_n: Number of EfficientNet tail layers to unfreeze in Phase 2.
    Side effects:
        Saves best model to {output_dir}/plant_disease_efficientnet.keras.
    """
    # Set mixed precision for faster training on GPU
    tf.keras.mixed_precision.set_global_policy("mixed_float16")

    # Build datasets
    train_ds, val_ds = build_datasets(
        data_dir=data_dir,
        input_size=input_size,
        batch_size=batch_size,
        num_classes=num_classes,
    )

    # Build model
    model = build_model(num_classes=num_classes, input_size=input_size)
    model.summary()

    callbacks = build_callbacks(output_dir)

    # ── Phase 1: Warm-up head only ───────────────────────────────────────────
    print("\n" + "="*60)
    print("PHASE 1: Training classification head (base frozen)")
    print("="*60)

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="categorical_crossentropy",
        metrics=[
            "accuracy",
            tf.keras.metrics.TopKCategoricalAccuracy(k=3, name="top3_accuracy"),
        ],
    )
    model.fit(
        train_ds,
        epochs=phase1_epochs,
        validation_data=val_ds,
        callbacks=callbacks,
    )

    # ── Phase 2: Fine-tune top N EfficientNet layers ─────────────────────────
    print("\n" + "="*60)
    print(f"PHASE 2: Fine-tuning top {unfreeze_last_n} EfficientNet layers")
    print("="*60)

    # Unfreeze the base model
    base_model = model.layers[1]  # EfficientNetB4 is layer index 1
    base_model.trainable = True

    # Freeze all but the last N layers
    for layer in base_model.layers[:-unfreeze_last_n]:
        layer.trainable = False

    trainable_count = sum(1 for l in base_model.layers if l.trainable)
    print(f"Trainable EfficientNet layers: {trainable_count}/{len(base_model.layers)}")

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
        loss="categorical_crossentropy",
        metrics=[
            "accuracy",
            tf.keras.metrics.TopKCategoricalAccuracy(k=3, name="top3_accuracy"),
        ],
    )
    model.fit(
        train_ds,
        epochs=phase2_epochs,
        validation_data=val_ds,
        callbacks=callbacks,
    )

    # Save final model
    final_path = os.path.join(output_dir, "plant_disease_efficientnet.keras")
    model.save(final_path)
    print(f"\n✓ Final model saved to {final_path}")

    # Print final validation accuracy
    val_results = model.evaluate(val_ds, verbose=1)
    print(f"\nFinal val accuracy: {val_results[1]:.4f}")
    print(f"Final val top-3 accuracy: {val_results[2]:.4f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train FasalDoc plant disease model")
    parser.add_argument("--data-dir", required=True, help="PlantVillage dataset root directory")
    parser.add_argument("--output-dir", default="models", help="Output directory for saved models")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--input-size", type=int, default=224)
    parser.add_argument("--phase1-epochs", type=int, default=5)
    parser.add_argument("--phase2-epochs", type=int, default=20)
    args = parser.parse_args()

    train(
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        batch_size=args.batch_size,
        input_size=args.input_size,
        phase1_epochs=args.phase1_epochs,
        phase2_epochs=args.phase2_epochs,
    )
