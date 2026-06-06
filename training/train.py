"""
Train a YOLOv8 model on the scorpion detection dataset.

Prerequisites
-------------
1. Download the dataset from Kaggle (see README.md for the link).
2. Unzip it so the structure matches:

       dataset/
           images/
               train/   *.jpg  *.png
               val/     *.jpg  *.png
           labels/
               train/   *.txt
               val/     *.txt

3. Download the dataset from https://www.kaggle.com/datasets/chibanimohamedali/scorpion-detection-dataset
4. Install dependencies:
       pip install ultralytics

Usage
-----
    python training/train.py --data dataset/data.yaml --epochs 100
"""

import argparse
from pathlib import Path

from ultralytics import YOLO


def parse_args():
    p = argparse.ArgumentParser(description="Train YOLO scorpion detector")
    p.add_argument("--model",   default="yolov8n.pt", help="Base YOLO model (yolov8n/s/m/l/x.pt)")
    p.add_argument("--data",    required=True,         help="Path to data.yaml")
    p.add_argument("--epochs",  type=int, default=100, help="Training epochs")
    p.add_argument("--imgsz",   type=int, default=640, help="Image size")
    p.add_argument("--batch",   type=int, default=16,  help="Batch size (-1 = auto)")
    p.add_argument("--project", default="runs/train",  help="Output directory")
    p.add_argument("--name",    default="scorpion",    help="Run name")
    p.add_argument("--device",  default="",            help="Device: '' (auto), 'cpu', '0', '0,1'")
    return p.parse_args()


def main():
    args = parse_args()

    model = YOLO(args.model)
    results = model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        project=args.project,
        name=args.name,
        device=args.device or None,
    )

    best = Path(results.save_dir) / "weights" / "best.pt"
    print(f"\nTraining complete. Best weights: {best}")
    print("Copy best.pt to models/ and create a GitHub Release to make it available:")
    print("  cp", best, "models/best.pt")


if __name__ == "__main__":
    main()
