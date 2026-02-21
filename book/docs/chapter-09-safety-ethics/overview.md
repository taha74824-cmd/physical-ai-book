---
sidebar_position: 1
title: Overview
---

# Chapter 9: Safety and Ethics in Physical AI

## Introduction

Physical AI systems operate in the real world where failures can cause physical harm. Ensuring their safety and ethical operation is paramount. This chapter examines both technical safety approaches and broader ethical considerations.

## Technical Safety

### Runtime Monitoring

```python
class SafetyMonitor:
    def __init__(self, robot):
        self.robot = robot
        self.safety_conditions = [
            self.check_joint_limits,
            self.check_velocity_limits,
            self.check_human_proximity,
        ]

    def step(self, proposed_action):
        for condition in self.safety_conditions:
            result = condition(self.robot.state, proposed_action)
            if result.is_unsafe:
                return self.safe_fallback(result.reason)
        return proposed_action

    def check_human_proximity(self, state, action):
        humans = self.robot.perception.detect_humans()
        for human in humans:
            if human.distance < 0.3:  # 30cm minimum
                return SafetyResult(is_unsafe=True, reason="human_too_close")
        return SafetyResult(is_unsafe=False)
```

### Control Barrier Functions (CBFs)

Mathematical framework guaranteeing safety: a barrier function B(x) ensures the robot stays within a safe set. Used in autonomous vehicles and collaborative robots.

### Safe Reinforcement Learning

```python
def safe_policy_update(policy, trajectories, safety_critic, lambda_safety):
    reward_gradient = compute_policy_gradient(policy, trajectories)
    safety_violations = safety_critic(trajectories)
    safety_gradient = compute_safety_gradient(policy, trajectories, safety_violations)

    total_gradient = reward_gradient - lambda_safety * safety_gradient
    policy.update(total_gradient)

    # Update Lagrange multiplier
    lambda_safety = max(0, lambda_safety + lr * (safety_violations.mean() - epsilon))
    return lambda_safety
```

## Human-Robot Safety Standards

### ISO 10218: Robots and Robotic Devices
- Risk assessment mandatory
- Protective stops required
- Force/torque limiting for collaborative operation

### ISO/TS 15066: Collaborative Robots

| Contact Mode | Power Limit | Force Limit |
|-------------|-------------|-------------|
| Transient | 80W | 250N |
| Quasi-static | 25W | 50N |

## Ethical Considerations

### Bias in Physical AI

Robots trained on biased data may behave unequally across demographic groups. Regular auditing for demographic parity is essential.

### Accountability Framework

Who is responsible when a Physical AI system causes harm?

- **Manufacturer**: Design defects
- **Deployer**: Misuse, inadequate training
- **Operator**: Improper supervision
- **Developer**: Algorithm errors

### Privacy

Physical AI systems in public spaces raise concerns:
- Robots with cameras in homes and offices
- Autonomous vehicles recording street activity
- Warehouse robots tracking worker movements

Privacy-preserving approaches:
- On-device processing (no data leaves the robot)
- Federated learning across robot fleets
- Differential privacy in collected data

### Autonomous Weapons

Lethal Autonomous Weapons Systems (LAWS) represent the most contentious application:

```
Key ethical positions:
- "Human in the loop": Human must authorize each lethal action
- "Human on the loop": Human can override autonomous decisions
- "Human out of the loop": Fully autonomous lethal action (opposed by ICRC)
```

## Value Alignment

### Constitutional AI (Anthropic)
1. Define a set of principles (a "constitution")
2. Train AI to critique and revise its outputs according to principles
3. Use AI feedback for RLHF

### Explainable Physical AI

```python
class ExplainableRobot:
    def decide_and_explain(self, situation):
        action = self.policy(situation)
        explanation = {
            "action": action,
            "reason": self.explain_action(situation, action),
            "confidence": self.get_confidence(situation, action),
            "safety_check": self.safety_monitor.check(situation, action)
        }
        return action, explanation
```

## Summary

Safety and ethics are not add-ons to Physical AI — they are fundamental requirements. As physical systems become more capable and widespread, engineers, ethicists, policymakers, and the public must work together to ensure Physical AI benefits all of humanity.
