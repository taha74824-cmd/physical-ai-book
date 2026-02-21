---
sidebar_position: 1
title: Overview
---

# Chapter 3: Machine Learning for Physical Systems

## Introduction

Machine learning has transformed Physical AI from a field of hand-crafted rules to one where systems learn from data and experience. This chapter covers the core ML techniques that power modern Physical AI.

## Supervised Learning in Robotics

### Object Detection

**YOLO** (You Only Look Once) enables real-time object detection:

```python
from ultralytics import YOLO

model = YOLO('yolov8n.pt')

for result in model.predict(camera_frame, conf=0.5):
    for box in result.boxes:
        class_name = result.names[int(box.cls)]
        confidence = float(box.conf)
        print(f"Detected: {class_name} ({confidence:.2f})")
```

## Reinforcement Learning (RL)

RL is perhaps the most important ML paradigm for Physical AI. An agent learns to maximize cumulative reward through interaction with the environment.

### The RL Framework

```
State (s) → Policy π(a|s) → Action (a) → Environment → Reward (r) + Next State (s')
```

### Key RL Algorithms

#### Proximal Policy Optimization (PPO)
Most commonly used for robot learning — stable and sample efficient.

#### Soft Actor-Critic (SAC)
Maximum entropy RL for continuous action spaces — excellent for robot manipulation.

### Reward Engineering

```python
def manipulation_reward(state, action, next_state):
    if is_task_complete(next_state):
        return 100.0
    progress = -distance_to_goal(next_state)
    energy_penalty = -0.01 * np.sum(action**2)
    collision_penalty = -50.0 if collision_detected(next_state) else 0.0
    return progress + energy_penalty + collision_penalty
```

## Imitation Learning

Learning from demonstration is often more practical than RL.

### Behavioral Cloning (BC)

```python
demonstrations = [(obs_1, action_1), (obs_2, action_2), ...]

for epoch in range(num_epochs):
    for obs, expert_action in demonstrations:
        predicted_action = policy(obs)
        loss = mse_loss(predicted_action, expert_action)
        optimizer.step()
```

**Limitation**: Distributional shift — robot encounters states not in demonstrations.

### DAgger (Dataset Aggregation)
Iteratively expands dataset with expert corrections, solving distributional shift.

## Diffusion Policy

Diffusion models used for robot imitation learning achieve state-of-the-art performance:

```python
def denoise_action(noisy_action, observation, timestep):
    predicted_noise = noise_predictor(noisy_action, observation, timestep)
    clean_action = (noisy_action - predicted_noise * sqrt_alpha_bar) / sqrt_alpha
    return clean_action
```

## World Models

World models learn a compressed representation of the environment for planning:

```python
class WorldModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = CNNEncoder()        # Image → latent state
        self.dynamics = RNNDynamics()      # Latent state + action → next latent
        self.reward_fn = RewardPredictor() # Latent state → reward

    def imagine(self, initial_state, actions):
        states = [initial_state]
        for action in actions:
            next_state = self.dynamics(states[-1], action)
            states.append(next_state)
        return states
```

Notable world models: DreamerV3, RSSM, TD-MPC2.

## Transfer Learning

### CLIP for Zero-Shot Object Detection

```python
import clip, torch

model, preprocess = clip.load("ViT-B/32")
text = clip.tokenize(["a red cube", "a blue sphere", "empty table"])
image_features = model.encode_image(camera_image)
text_features = model.encode_text(text)
similarity = (image_features @ text_features.T).softmax(dim=-1)
```

## Summary

Machine learning provides Physical AI systems with the ability to learn from data, adapt to new situations, and improve over time. From supervised learning for perception to reinforcement learning for control to world models for planning, ML is the engine that drives modern physical systems.

## Review Questions

1. What is the fundamental difference between reinforcement learning and supervised learning?
2. Why is reward engineering challenging in physical AI systems?
3. What are the advantages of imitation learning over RL?
4. How do world models enable more efficient learning?
