---
sidebar_position: 1
title: Overview
---

# Chapter 4: Computer Vision in Physical AI

## Introduction

Computer vision is the sensory organ of Physical AI. Without the ability to see and interpret the world, robots would be blind to the rich visual information that humans rely on for nearly every task.

## Camera Models and Calibration

### Pinhole Camera Model

```
[u]   [fx  0  cx] [X]
[v] = [0  fy  cy] [Y] / Z
[1]   [0   0   1] [Z]
```

Where (u,v) are pixel coordinates and (X,Y,Z) are 3D world coordinates.

### Camera Calibration

```python
import cv2

# Find checkerboard corners
ret, corners = cv2.findChessboardCorners(gray_image, (9, 6), None)

# Compute calibration matrix
ret, K, dist, rvecs, tvecs = cv2.calibrateCamera(
    objpoints, imgpoints, gray_image.shape[::-1], None, None
)
```

## 3D Vision: Depth Estimation

### Stereo Vision

```
Depth Z = (focal_length × baseline) / disparity
```

```python
stereo = cv2.StereoBM_create(numDisparities=96, blockSize=15)
disparity = stereo.compute(left_gray, right_gray).astype(np.float32) / 16.0
depth_map = (focal_length * baseline) / disparity
```

### Monocular Depth Estimation

```python
from transformers import pipeline
depth_estimator = pipeline("depth-estimation", model="Intel/dpt-large")
depth = depth_estimator(image)
```

Notable models: MiDaS, DPT, ZoeDepth, Depth-Anything.

## Object Detection

### YOLO (Real-time Detection)

```python
from ultralytics import YOLO

model = YOLO('yolov8n.pt')
for result in model.track(source=0, stream=True):
    annotated_frame = result.plot()
    cv2.imshow('Robot Camera', annotated_frame)
```

### DETR (Detection Transformer)

End-to-end detection without anchor boxes using cross-attention.

## Segment Anything Model (SAM)

Foundation model for segmentation:

```python
from segment_anything import sam_model_registry, SamPredictor

sam = sam_model_registry["vit_h"](checkpoint="sam_vit_h.pth")
predictor = SamPredictor(sam)
predictor.set_image(image)

masks, scores, logits = predictor.predict(
    point_coords=np.array([[x, y]]),
    point_labels=np.array([1]),
    multimask_output=True
)
```

## 6DoF Pose Estimation

Determining position AND orientation of objects — critical for manipulation:

```python
# Solve PnP (Perspective-n-Point)
success, rvec, tvec = cv2.solvePnP(
    points_3d, points_2d, camera_matrix, dist_coeffs
)
rotation_matrix, _ = cv2.Rodrigues(rvec)
```

## LiDAR Point Cloud Processing

```python
import open3d as o3d

pcd = o3d.io.read_point_cloud("scan.pcd")
pcd_down = pcd.voxel_down_sample(voxel_size=0.05)

# Ground plane segmentation
plane_model, inliers = pcd_down.segment_plane(
    distance_threshold=0.01, ransac_n=3, num_iterations=1000
)
```

## Foundation Models for Vision

### CLIP (Zero-Shot Recognition)

```python
import clip, torch

model, preprocess = clip.load("ViT-B/32", device="cuda")
text_prompts = ["a cup", "a book", "a phone", "a key"]
text = clip.tokenize(text_prompts).to("cuda")

with torch.no_grad():
    image_features = model.encode_image(preprocess(image).unsqueeze(0).to("cuda"))
    text_features = model.encode_text(text)
    similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
```

### Grounding DINO
Open-vocabulary object detection — detect any object described in natural language.

### DINOv2
Visual features without supervision — powerful for downstream robotics tasks.

## Summary

Computer vision provides Physical AI systems with the rich visual understanding needed to perceive and interact with the physical world. From basic image processing to sophisticated foundation models, the field has advanced dramatically and continues to enable more capable robotic systems.
