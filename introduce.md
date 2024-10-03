# Project Introduction

## The name of the project
Biomimicry

## Project Overview
This project is a creature simulation program based on the Pygame library that shows a simple ecosystem with two main mobs: blue orbs (students) and red orbs (predators). Students move around the scene, get oxygen, and reproduce with other blue orbs, while predators chase and capture the blue orbs, creating a dynamic ecological balance.

## Key features
1. **Producer (Blue Ball)**
   - Each student has their own position, velocity, direction, perceptual radius, and oxygen storage.
   - Move randomly and collect oxygen while avoiding predators.
   - New producers can be created through reproduction

2. **Predator (Red Ball)**
   - The predator chases the nearest student.
   - Capturing a student increases their own capture count and releases oxygen.
   - There is a certain breeding mechanism that is able to spawn new predators.

3. **Ecological characteristics**
   - Oxygen is a resource that restricts the reproduction and survival of living things.
   - The change of seasons affects the speed at which the blue ball moves.
   - Through the design of collision and reproduction mechanisms, the dynamic evolution of ecosystems is simulated.

## Technical details
- Use the Python language in combination with the Pygame library to implement a graphical interface and animations.
- Random number generation is used to simulate the behavior, speed, and reproduction of living creatures.
- Physics algorithms are used to detect collisions, boundaries, and relationships between organisms (alignment, separation, aggregation behavior).

## How to use
1. Install the Pygame library:
   ```bash
   pip install pygame
2. Run the program
   ```bash
   python main.py
In the window, you can toggle the debugging mode by pressing the D (English mode) key to view the detailed data of the creature.

## Target
Through this biosimulation project, it is hoped that self-organizing behaviors will be demonstrated to help understand fundamental concepts in ecology, interactions, and resource management. It also provides a basic platform for further algorithmic research (e.g., group behavior, ecological balance).

## Last
This is just a rough project.So if you find some bug, plse let me know.