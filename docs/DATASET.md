# Scorpion Detection Dataset

## Overview

A single-class object-detection dataset for training and evaluating scorpion detectors.
It contains **1,412 images** annotated in **YOLO TXT format** — the same format consumed
directly by the Ultralytics training pipeline.

The dataset is hosted publicly on Kaggle:
> **[Scorpion Detection Dataset on Kaggle](https://www.kaggle.com/datasets/chibanimohamedali/scorpion-detection-dataset)**

---

## Contents

| Split | Images | Labels |
|-------|-------:|-------:|
| Train | 1,263  | 1,264  |
| Val   |   149  |   150  |
| **Total** | **1,412** | **1,414** |

### Classes

| ID | Name     |
|----|----------|
| 0  | scorpion |

A single class is used; all annotations refer to scorpions regardless of species.

---

## Label Format

Labels follow the **YOLO TXT** format — one `.txt` file per image, same base name:

```
<class_id> <cx> <cy> <width> <height>
```

All coordinates are **normalised** to `[0, 1]` relative to the image dimensions.
Multi-instance images have one annotation per line.

**Example** (`s1093.txt`):
```
0 0.421185 0.567158 0.114089 0.054330
```

---

## Image Formats

| Format | Count |
|--------|------:|
| JPEG   | 1,252 |
| PNG    |   160 |

Images vary in resolution; the training pipeline resizes to 640 × 640 by default.

---

## Collection & Annotation

Images were collected from publicly available sources and annotated manually using
bounding boxes drawn around visible scorpions.  The dataset covers a variety of
backgrounds (desert sand, rock, indoor surfaces) and lighting conditions to improve
model generalisation.

---

## Intended Use

- Training and fine-tuning YOLO-family object detectors for scorpion detection.
- Benchmarking detection models in a single-class, small-object setting.
- Public-health and safety applications in regions (particularly North Africa) where
  scorpion stings are a significant health risk.

---

## Licensing

This dataset is released under the **Creative Commons Attribution 4.0 International
(CC BY 4.0)** licence.  You are free to use, adapt, and redistribute it for any purpose,
provided appropriate credit is given to **CHIBANI Mohamed Ali**.

See <https://creativecommons.org/licenses/by/4.0/> for the full licence text.

---

## Citation

If you use this dataset in research or a project, please cite:

```
CHIBANI Mohamed Ali. Scorpion Detection Dataset (2024).
Available on Kaggle: https://www.kaggle.com/datasets/chibanimohamedali/scorpion-detection-dataset
```
