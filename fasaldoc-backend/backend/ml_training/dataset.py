"""
Dataset loader for PlantVillage directory format.
Applies albumentations augmentation pipeline during training.
"""
import os
import numpy as np
import tensorflow as tf
from pathlib import Path


def build_datasets(
    data_dir: str,
    input_size: int = 224,
    batch_size: int = 32,
    num_classes: int = 38,
    validation_split: float = 0.2,
    seed: int = 42,
) -> tuple:
    """
    Build train and validation tf.data.Dataset from PlantVillage directory.
    Applies augmentation to training set only.

    Args:
        data_dir: Root directory with one subdirectory per class.
        input_size: Target image size (square).
        batch_size: Batch size for both train and val.
        num_classes: Total number of classes.
        validation_split: Fraction of data for validation.
        seed: Random seed for reproducible splits.
    Returns:
        Tuple of (train_ds, val_ds) tf.data.Dataset instances.
    """
    train_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=validation_split,
        subset="training",
        seed=seed,
        image_size=(input_size, input_size),
        batch_size=batch_size,
        label_mode="categorical",
        shuffle=True,
    )

    val_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=validation_split,
        subset="validation",
        seed=seed,
        image_size=(input_size, input_size),
        batch_size=batch_size,
        label_mode="categorical",
        shuffle=False,
    )

    # Normalize to [-1, 1] for EfficientNet
    def normalize(images, labels):
        images = tf.cast(images, tf.float32)
        images = (images / 127.5) - 1.0
        return images, labels

    # Augmentation layer for training
    augmentation_layer = tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal_and_vertical"),
        tf.keras.layers.RandomRotation(0.25),
        tf.keras.layers.RandomZoom(0.15),
        tf.keras.layers.RandomBrightness(0.2),
        tf.keras.layers.RandomContrast(0.2),
    ], name="augmentation")

    def augment_and_normalize(images, labels):
        images = augmentation_layer(images, training=True)
        images = tf.cast(images, tf.float32)
        images = (images / 127.5) - 1.0
        return images, labels

    AUTOTUNE = tf.data.AUTOTUNE

    train_ds = (
        train_ds
        .map(augment_and_normalize, num_parallel_calls=AUTOTUNE)
        .prefetch(AUTOTUNE)
    )

    val_ds = (
        val_ds
        .map(normalize, num_parallel_calls=AUTOTUNE)
        .prefetch(AUTOTUNE)
    )

    return train_ds, val_ds


def get_class_names(data_dir: str) -> list[str]:
    """
    Return sorted list of class names from directory structure.

    Args:
        data_dir: Root PlantVillage directory.
    Returns:
        Sorted list of class name strings.
    """
    return sorted([
        d for d in os.listdir(data_dir)
        if os.path.isdir(os.path.join(data_dir, d))
    ])


def compute_class_weights(data_dir: str) -> dict[int, float]:
    """
    Compute inverse-frequency class weights to handle dataset imbalance.

    Args:
        data_dir: Root PlantVillage directory.
    Returns:
        Dict mapping class index to weight float.
    """
    class_names = get_class_names(data_dir)
    counts = {}
    for idx, cls in enumerate(class_names):
        cls_path = Path(data_dir) / cls
        counts[idx] = len(list(cls_path.glob("*.jpg")) + list(cls_path.glob("*.JPG")) + list(cls_path.glob("*.png")))

    total = sum(counts.values())
    n_classes = len(counts)
    weights = {idx: total / (n_classes * count) for idx, count in counts.items() if count > 0}
    return weights
