---
sidebar_position: 1
title: Overview
---

# Chapter 6: Sim-to-Real Transfer

## Introduction

Training robots in the real world is expensive, slow, and potentially dangerous. Simulation offers a safe, fast, and scalable alternative — but simulated robots often fail when deployed in the real world. Bridging this "reality gap" is one of the central challenges of Physical AI.

## The Reality Gap

The reality gap refers to the discrepancy between simulated and real environments. Key sources:

### Physics Modeling Errors
- **Contact dynamics**: Friction and contact behavior are notoriously hard to simulate accurately
- **Deformable objects**: Cloth, food, and soft materials resist accurate simulation
- **Actuator dynamics**: Real motors have backlash, compliance, and nonlinearities

### Sensor Modeling Errors
- **Visual appearance**: Simulated textures differ from real materials
- **Sensor noise**: Real sensors have complex noise distributions
- **Lighting**: Global illumination and shadows are hard to replicate

## Domain Randomization

Domain Randomization (DR) is the most widely used technique for sim-to-real transfer. The key insight: if training exposes the robot to enough variation, real-world conditions become just another variation.

```python
class DomainRandomizer:
    def randomize_environment(self, env):
        # Randomize physics
        env.set_friction(np.random.uniform(0.5, 2.0))
        env.set_mass_multiplier(np.random.uniform(0.8, 1.2))

        # Randomize visual appearance
        env.randomize_textures()
        env.randomize_lighting(
            intensity=np.random.uniform(0.5, 2.0),
            direction=np.random.uniform(0, 2*np.pi)
        )

        # Randomize object positions
        for obj in env.objects:
            obj.position += np.random.normal(0, 0.05, size=3)

        return env
```

### Automatic Domain Randomization (ADR)

OpenAI's Dactyl hand used ADR to learn dexterous manipulation entirely in simulation:
1. Start with low randomization
2. Track robot performance
3. Increase randomization when robot succeeds
4. Decrease when robot fails consistently

## System Identification

System identification improves the simulation by calibrating it to match the real robot:

```python
def system_identification(real_robot, simulator, test_sequences):
    real_trajectories = [real_robot.execute(seq) for seq in test_sequences]

    def simulation_error(params):
        simulator.set_params(params)
        total_error = sum(
            trajectory_distance(real_traj, simulator.rollout(actions))
            for actions, real_traj in zip(test_sequences, real_trajectories)
        )
        return total_error

    from scipy.optimize import minimize
    optimal_params = minimize(simulation_error, simulator.get_params())
    simulator.set_params(optimal_params)
    return simulator
```

## Online Adaptation

### RMA (Rapid Motor Adaptation)

Trains an adaptation module that infers environment parameters from recent history — enabling real-time adaptation during deployment.

### Meta-Learning (MAML)

Train a policy that can quickly adapt to new environments:
- Inner loop: adapt to specific environment
- Outer loop: optimize for fast adaptation

## Photorealistic Simulation

### NVIDIA Isaac Sim

```python
from omni.isaac.kit import SimulationApp
from omni.isaac.core import World

simulation_app = SimulationApp({"headless": False})
world = World(stage_units_in_meters=1.0)
world.scene.add_default_ground_plane()
world.reset()

for i in range(1000):
    world.step(render=True)
```

### Genesis

A new GPU-accelerated physics simulation platform:
- Multi-physics: rigid, fluid, cloth, soft bodies
- Differentiable simulation
- Thousands of parallel environments

## Benchmark Results

| Task | Method | Sim Success | Real Success |
|------|---------|-------------|--------------|
| Rubik's Cube (1-handed) | OpenAI Dactyl + DR | 95% | 20% |
| Legged locomotion | ETH Anymal | 99% | 95% |
| Object grasping | QT-Opt | N/A | 96% |

## Summary

Sim-to-real transfer is essential for scalable Physical AI development. Techniques like domain randomization, system identification, and adaptive methods continue to close the reality gap, making simulation an increasingly reliable proxy for real-world training.
