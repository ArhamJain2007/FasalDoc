"""
Albumentations-based augmentation pipeline for plant disease detection.
Used during training to improve model generalization on Indian field conditions.
"""
import numpy as np
import albumentations as A
from albumentations.pytorch import ToTensorV2


def build_augmentation_pipeline(input_size: int = 224) -> A.Compose:
    """
    Build an aggressive albumentations augmentation pipeline.
    Designed to simulate real-world Indian field image variability:
    lighting variation, leaf orientation, partial occlusion, camera blur.

    Args:
        input_size: Target output image size (square).
    Returns:
        albumentations.Compose transform pipeline.
    """
    return A.Compose([
        A.RandomRotate90(p=0.5),
        A.HorizontalFlip(p=0.5),
        A.VerticalFlip(p=0.3),
        A.RandomBrightnessContrast(
            brightness_limit=0.2,
            contrast_limit=0.2,
            p=0.6,
        ),
        A.HueSaturationValue(
            hue_shift_limit=20,
            sat_shift_limit=30,
            val_shift_limit=20,
            p=0.5,
        ),
        A.GaussianBlur(
            blur_limit=(3, 7),
            p=0.3,
        ),
        A.GridDistortion(
            num_steps=5,
            distort_limit=0.2,
            p=0.3,
        ),
        A.CoarseDropout(
            max_holes=8,
            max_height=32,
            max_width=32,
            min_holes=1,
            fill_value=0,
            p=0.3,
        ),
        A.ShiftScaleRotate(
            shift_limit=0.1,
            scale_limit=0.15,
            rotate_limit=30,
            border_mode=0,
            p=0.5,
        ),
        A.CLAHE(
            clip_limit=4.0,
            tile_grid_size=(8, 8),
            p=0.3,
        ),
        A.Resize(input_size, input_size),
        A.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ])


def build_val_pipeline(input_size: int = 224) -> A.Compose:
    """
    Minimal validation/inference pipeline: resize + normalize only.

    Args:
        input_size: Target image size.
    Returns:
        albumentations.Compose with resize and normalize.
    """
    return A.Compose([
        A.Resize(input_size, input_size),
        A.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ])


def apply_augmentation(image: np.ndarray, pipeline: A.Compose) -> np.ndarray:
    """
    Apply an albumentations pipeline to a single numpy image.

    Args:
        image: np.ndarray of shape (H, W, 3), dtype uint8.
        pipeline: Compiled albumentations Compose pipeline.
    Returns:
        Augmented np.ndarray of shape (H, W, 3).
    """
    result = pipeline(image=image)
    return result["image"]
