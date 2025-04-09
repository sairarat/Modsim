import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Configuration
incident_angles_deg = [10.6, 24.1]  # Incident angles
surface_x = 0  # Vertical surface (normal is 0°)
candle_y = 1.5
eye_x = 5
eye_y = 3

# Set up plot
fig, ax = plt.subplots(figsize=(10, 5))
ax.set_aspect('equal')

# Draw vertical rough surface (center mirror)
rough_y = np.linspace(0.5, 4.5, 100)
rough_x = surface_x + 0.1 * np.random.uniform(-1, 1, size=rough_y.shape)
ax.plot(rough_x, rough_y, color='black', linewidth=2)

# Draw candle
candle_x = -4
candle_height = 1
flame_y = candle_y + candle_height
ax.add_patch(patches.Rectangle((candle_x - 0.3, candle_y - 0.2), 0.6, candle_height, color='gold'))
ax.plot(candle_x, flame_y, marker='o', color='red', markersize=10)

# Draw observer
eye = patches.Circle((eye_x, eye_y), 0.5, fill=False, edgecolor='black', linewidth=2)
ax.add_patch(eye)
ax.plot(eye_x - 0.2, eye_y, marker='o', color='black', markersize=5)

# Draw rays and calculate reflection angles
for angle_deg in incident_angles_deg:
    angle_rad = np.radians(angle_deg)

    # Incident ray: from candle to mirror
    in_y_end = flame_y + (surface_x - candle_x) * np.tan(angle_rad)
    ax.plot([candle_x, surface_x], [flame_y, in_y_end], color='brown', linestyle='--')
    ax.text((candle_x + surface_x) / 2 - 0.5, (flame_y + in_y_end) / 2 + 0.2, f"{angle_deg}°", fontsize=8, color='brown')

    # Base reflected angle (ideal case without scatter)
    reflected_base_deg = -angle_deg  # Since surface normal is vertical (0°), reflection = -incident

    # Scattered reflected rays
    for i in range(5):
        scatter_offset = np.random.uniform(-0.1, 0.1)
        scatter_y = in_y_end + scatter_offset

        scatter_deviation = np.random.uniform(-30, 30)
        scatter_angle_deg = reflected_base_deg + scatter_deviation
        scatter_rad = np.radians(scatter_angle_deg)

        ray_len = 6
        dx = ray_len * np.cos(scatter_rad)
        dy = ray_len * np.sin(scatter_rad)

        end_x = surface_x + dx
        end_y = scatter_y + dy

        ax.plot([surface_x, end_x], [scatter_y, end_y], color='gold', alpha=0.6)

        # Show angle label
        ax.text(surface_x + dx * 0.4, scatter_y + dy * 0.4, f"{scatter_angle_deg:.1f}°", fontsize=7, color='gray')

# Virtual image
ax.add_patch(patches.Rectangle((-candle_x - 0.3, candle_y - 0.2), 0.6, candle_height, color='gold', alpha=0.3))
ax.plot(-candle_x, flame_y, marker='o', color='red', markersize=10, alpha=0.3)

# Labels
ax.text(candle_x, candle_y - 0.5, "Candle", ha='center')
ax.text(-candle_x, candle_y - 0.5, "Virtual Image", ha='center', fontsize=9)
ax.text(eye_x, eye_y + 0.7, "Observer", ha='center')
ax.text(0, 0.3, "Rough Surface / Mirror", ha='center', fontsize=9)

# Layout
ax.axvline(x=0, color='black', linestyle='-')  # central vertical mirror
ax.set_xlim(-6, 6)
ax.set_ylim(0, 5)
ax.axis('off')
plt.title("Diffuse Reflection on Vertical Rough Surface (with Calculated Angles)", fontsize=14)
plt.show()
