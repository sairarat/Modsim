import matplotlib.pyplot as plt
import numpy as np
import math

# Define the positions
candle_pos = np.array([750, 280])
mirror_x = 450
eye_pos = np.array([800, 80])

# Find the point on the mirror where the ray hits
def find_mirror_point(candle_pos, eye_pos, mirror_x):
    x1, y1 = candle_pos
    x2, y2 = eye_pos
    t = (mirror_x - x1) / (x2 - x1)
    y = y1 + t * (y2 - y1)
    return np.array([mirror_x, y])

# Calculate angle between two vectors
def calculate_angle(v1, v2):
    dot_product = np.dot(v1, v2)
    magnitude_v1 = np.linalg.norm(v1)
    magnitude_v2 = np.linalg.norm(v2)
    cos_theta = dot_product / (magnitude_v1 * magnitude_v2)
    angle_rad = np.arccos(np.clip(cos_theta, -1.0, 1.0))  # Clamp to avoid rounding errors
    return np.degrees(angle_rad)

# Calculate the mirror point
mirror_point = find_mirror_point(candle_pos, eye_pos, mirror_x)

# Incident ray vector (from candle to mirror)
incident_ray = mirror_point - candle_pos
# Normal vector (horizontal, pointing left)
normal_vector = np.array([1, 0])
# Reflected ray vector (from mirror to eye)
reflected_ray = eye_pos - mirror_point

# Calculate angles
incident_angle = calculate_angle(incident_ray, normal_vector)
reflected_angle = incident_angle  # By the law of reflection

# Plotting the vectors
fig, ax = plt.subplots()
ax.set_xlim(400, 850)
ax.set_ylim(0, 450)

# Plot mirror line
ax.plot([mirror_x, mirror_x], [0, 450], color='black', linewidth=2)

# Plot the rays
ax.quiver(candle_pos[0], candle_pos[1], incident_ray[0], incident_ray[1], angles='xy', scale_units='xy', scale=1, color='red', label="Incident Ray")
ax.quiver(mirror_point[0], mirror_point[1], reflected_ray[0], reflected_ray[1], angles='xy', scale_units='xy', scale=1, color='blue', label="Reflected Ray")
ax.quiver(mirror_point[0], mirror_point[1], normal_vector[0], normal_vector[1], angles='xy', scale_units='xy', scale=1, color='green', label="Normal")

# Plot the candle and the eye
ax.plot(candle_pos[0], candle_pos[1], 'yo', label="Candle")
ax.plot(eye_pos[0], eye_pos[1], 'wo', label="Eye")

# Display the angles
ax.text(mirror_x + 10, mirror_point[1], f"{incident_angle:.1f}°", color='black')
ax.text(mirror_x + 10, mirror_point[1] - 10, f"{reflected_angle:.1f}°", color='black')

# Set labels and show plot
ax.legend()
ax.set_aspect('equal')
plt.title("Reflection of Light Rays")
plt.show()
