import asyncio
import platform
import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 900, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Reflection Simulation with Toggle")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
GRAY = (200, 200, 200)
LIGHT_GRAY = (220, 220, 220)
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (100, 149, 237)

# Font
font = pygame.font.SysFont("arial", 16)

# UI positions
button_rect = pygame.Rect(10, 10, 250, 40)
button_label_smooth = font.render("Reflection on a Rough Surface", True, BLACK)
button_label_rough = font.render("Return to Smooth Reflection", True, BLACK)
simulation_mode = "rough"  # Default mode (start in rough mode)

# Object positions (smooth mode)
mirror_x = 450
real_pos_smooth = [750, 280]
image_pos = [150, 280]
eye_pos = [800, 80]
candle_size = (20, 60)
eye_size = (40, 40)

# Object positions (rough mode)
mirror_y = 250
real_pos_rough = [450, 100]

# Mirror points for rough surface
mirror_points = [(x, mirror_y + random.randint(-20, 20)) for x in range(0, WIDTH + 1, 20)]
mirror_points = [(0, mirror_y)] + mirror_points + [(WIDTH, mirror_y)]

dragging = None
offset_x, offset_y = 0, 0

# Grid settings
GRID_SIZE = 50

# Opacity settings
RAY_OPACITY = 128  # 50% opacity (out of 255)

def draw_grid():
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, LIGHT_GRAY, (x, 0), (x, HEIGHT), 1)
        label = font.render(str(x), True, BLACK)
        screen.blit(label, (x, HEIGHT - 20))
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, LIGHT_GRAY, (0, y), (WIDTH, y), 1)
        label = font.render(str(y), True, BLACK)
        screen.blit(label, (5, y))

def draw_dashed_line(surface, color, start, end, dash_length=10):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = math.sqrt(dx**2 + dy**2)
    if distance == 0:
        return
    dx /= distance
    dy /= distance
    num_dashes = int(distance / dash_length)
    for i in range(0, num_dashes, 2):
        start_x = start[0] + i * dash_length * dx
        start_y = start[1] + i * dash_length * dy
        end_x = start[0] + (i + 1) * dash_length * dx
        end_y = start[1] + (i + 1) * dash_length * dy
        pygame.draw.line(surface, color, (start_x, start_y), (end_x, end_y), 2)

# Smooth mirror functions
def find_mirror_point_smooth(start, end, mirror_x):
    x1, y1 = start
    x2, y2 = end
    if x2 == x1:
        return (mirror_x, y1)
    t = (mirror_x - x1) / (x2 - x1)
    y = y1 + t * (y2 - y1)
    return (mirror_x, y)

def calculate_angle_smooth(incident_point, mirror_point, reflected_point):
    normal = (1, 0)
    incident = (mirror_point[0] - incident_point[0], mirror_point[1] - incident_point[1])
    incident_magnitude = math.sqrt(incident[0]**2 + incident[1]**2)
    if incident_magnitude == 0:
        return 0
    incident = (incident[0] / incident_magnitude, incident[1] / incident_magnitude)
    dot_product = incident[0] * normal[0] + incident[1] * normal[1]
    angle = math.degrees(math.acos(abs(dot_product)))
    return angle

def reflect_ray_outside_smooth(incident_point, mirror_point, angle_of_incidence):
    normal = (1, 0)
    incident = (mirror_point[0] - incident_point[0], mirror_point[1] - incident_point[1])
    incident_magnitude = math.sqrt(incident[0]**2 + incident[1]**2)
    if incident_magnitude == 0:
        return (0, 0)
    incident = (incident[0] / incident_magnitude, incident[1] / incident_magnitude)
    dot_product = incident[0] * normal[0] + incident[1] * normal[1]
    reflected = (
        incident[0] - 2 * dot_product * normal[0],
        incident[1] - 2 * dot_product * normal[1]
    )
    return reflected

# Rough surface functions
def find_mirror_point_rough(start, end):
    x1, y1 = start
    x2, y2 = end
    if y2 == y1:
        return None
    closest_point = None
    min_distance = float('inf')
    
    for i in range(len(mirror_points) - 1):
        x3, y3 = mirror_points[i]
        x4, y4 = mirror_points[i + 1]
        
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(denom) < 1e-10:
            continue
        
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
        
        if 0 <= t <= 1 and 0 <= u <= 1:
            px = x1 + t * (x2 - x1)
            py = y1 + t * (y2 - y1)
            distance = math.sqrt((px - x1)**2 + (py - y1)**2)
            if distance < min_distance:
                min_distance = distance
                closest_point = (px, py, i)
    
    return closest_point

def get_segment_normal(segment_index):
    x1, y1 = mirror_points[segment_index]
    x2, y2 = mirror_points[segment_index + 1]
    dx = x2 - x1
    dy = y2 - y1
    length = math.sqrt(dx**2 + dy**2)
    if length == 0:
        return (0, 1)
    normal = (-dy / length, dx / length)
    return normal

def calculate_angle_rough(incident_point, mirror_point, reflected_direction, segment_index):
    normal = get_segment_normal(segment_index)
    incident = (mirror_point[0] - incident_point[0], mirror_point[1] - incident_point[1])
    incident_magnitude = math.sqrt(incident[0]**2 + incident[1]**2)
    if incident_magnitude == 0:
        return 0, 0
    incident = (incident[0] / incident_magnitude, incident[1] / incident_magnitude)
    reflected_magnitude = math.sqrt(reflected_direction[0]**2 + reflected_direction[1]**2)
    if reflected_magnitude == 0:
        return 0, 0
    reflected = (reflected_direction[0] / reflected_magnitude, reflected_direction[1] / reflected_magnitude)
    dot_product_incident = incident[0] * normal[0] + incident[1] * normal[1]
    angle_incident = math.degrees(math.acos(abs(dot_product_incident)))
    dot_product_reflected = reflected[0] * normal[0] + reflected[1] * normal[1]  # Fixed typo here
    angle_reflected = math.degrees(math.acos(abs(dot_product_reflected)))
    return angle_incident, angle_reflected

def reflect_ray_outside_rough(incident_point, mirror_point, segment_index):
    normal = get_segment_normal(segment_index)
    incident = (mirror_point[0] - incident_point[0], mirror_point[1] - incident_point[1])
    incident_magnitude = math.sqrt(incident[0]**2 + incident[1]**2)
    if incident_magnitude == 0:
        return [(0, 0)]
    incident = (incident[0] / incident_magnitude, incident[1] / incident_magnitude)
    dot_product = incident[0] * normal[0] + incident[1] * normal[1]
    
    # Specular reflection: R = I - 2(I·N)N
    specular_reflected = (
        incident[0] - 2 * dot_product * normal[0],
        incident[1] - 2 * dot_product * normal[1]
    )
    
    # Organized reflection: 4 rays at fixed angles relative to specular reflection
    reflected_rays = []
    num_rays = 4
    angles = [math.radians(-30), math.radians(-10), math.radians(10), math.radians(30)]
    for angle in angles:
        cos_theta = math.cos(angle)
        sin_theta = math.sin(angle)
        rotated_reflected = (
            specular_reflected[0] * cos_theta - specular_reflected[1] * sin_theta,
            specular_reflected[0] * sin_theta + specular_reflected[1] * cos_theta
        )
        reflected_rays.append(rotated_reflected)
    return reflected_rays

def setup():
    global screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Reflection Simulation with Toggle")

async def update_loop():
    global dragging, offset_x, offset_y, real_pos_smooth, image_pos, eye_pos, real_pos_rough, simulation_mode
    clock = pygame.time.Clock()

    # Create a surface for drawing rays with opacity
    ray_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    while True:
        screen.fill(LIGHT_BLUE)
        draw_grid()

        # Clear the ray surface for this frame
        ray_surface.fill((0, 0, 0, 0))

        # Draw the button
        button_label = button_label_rough if simulation_mode == "rough" else button_label_smooth
        pygame.draw.rect(screen, LIGHT_GRAY, button_rect)
        screen.blit(button_label, (button_rect.x + 10, button_rect.y + 10))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if button_rect.collidepoint(mouse_pos):
                    simulation_mode = "smooth" if simulation_mode == "rough" else "rough"
                    if simulation_mode == "smooth":
                        real_pos_smooth = [750, 280]
                        image_pos = [150, 280]
                        eye_pos = [800, 80]
                    else:
                        real_pos_rough = [450, 100]
                elif (real_pos_smooth[0] - candle_size[0]//2 <= mouse_pos[0] <= real_pos_smooth[0] + candle_size[0]//2 and
                      real_pos_smooth[1] <= mouse_pos[1] <= real_pos_smooth[1] + candle_size[1]):
                    dragging = "real_smooth"
                    offset_x = mouse_pos[0] - real_pos_smooth[0]
                    offset_y = mouse_pos[1] - real_pos_smooth[1]
                elif (image_pos[0] - candle_size[0]//2 <= mouse_pos[0] <= image_pos[0] + candle_size[0]//2 and
                      image_pos[1] <= mouse_pos[1] <= image_pos[1] + candle_size[1]):
                    dragging = "image"
                    offset_x = mouse_pos[0] - image_pos[0]
                    offset_y = mouse_pos[1] - image_pos[1]
                elif (eye_pos[0] - eye_size[0]//2 <= mouse_pos[0] <= eye_pos[0] + eye_size[0]//2 and
                      eye_pos[1] - eye_size[1]//2 <= mouse_pos[1] <= eye_pos[1] + eye_size[1]//2):
                    dragging = "eye"
                    offset_x = mouse_pos[0] - eye_pos[0]
                    offset_y = mouse_pos[1] - eye_pos[1]
                elif (real_pos_rough[0] - candle_size[0]//2 <= mouse_pos[0] <= real_pos_rough[0] + candle_size[0]//2 and
                      real_pos_rough[1] <= mouse_pos[1] <= real_pos_rough[1] + candle_size[1]):
                    dragging = "real_rough"
                    offset_x = mouse_pos[0] - real_pos_rough[0]
                    offset_y = mouse_pos[1] - real_pos_rough[1]
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = None
            elif event.type == pygame.MOUSEMOTION and dragging:
                mouse_pos = pygame.mouse.get_pos()
                if dragging == "real_smooth":
                    real_pos_smooth[0] = max(mirror_x + 50, min(850, mouse_pos[0] - offset_x))
                    real_pos_smooth[1] = max(0, min(HEIGHT - 100, mouse_pos[1] - offset_y))
                    image_pos[0] = mirror_x - (real_pos_smooth[0] - mirror_x)
                    image_pos[1] = real_pos_smooth[1]
                elif dragging == "image":
                    image_pos[0] = max(50, min(mirror_x - 50, mouse_pos[0] - offset_x))
                    image_pos[1] = max(0, min(HEIGHT - 100, mouse_pos[1] - offset_y))
                    real_pos_smooth[0] = mirror_x + (mirror_x - image_pos[0])
                    real_pos_smooth[1] = image_pos[1]
                elif dragging == "eye":
                    eye_pos[0] = max(mirror_x + 50, min(850, mouse_pos[0] - offset_x))
                    eye_pos[1] = max(50, min(HEIGHT - 50, mouse_pos[1] - offset_y))
                elif dragging == "real_rough":
                    real_pos_rough[0] = max(50, min(WIDTH - 50, mouse_pos[0] - offset_x))
                    real_pos_rough[1] = max(50, min(mirror_y - 50, mouse_pos[1] - offset_y))

        if simulation_mode == "smooth":
            # Draw the mirror
            pygame.draw.line(screen, BLACK, (mirror_x, 0), (mirror_x, HEIGHT), 4)

            # Draw the candle (real and image)
            pygame.draw.rect(screen, YELLOW, (real_pos_smooth[0] - candle_size[0]//2, real_pos_smooth[1], candle_size[0], candle_size[1]))
            pygame.draw.rect(screen, RED, (real_pos_smooth[0] - 5, real_pos_smooth[1] - 10, 10, 10))
            pygame.draw.rect(screen, YELLOW, (image_pos[0] - candle_size[0]//2, image_pos[1], candle_size[0], candle_size[1]), 2)
            pygame.draw.rect(screen, RED, (image_pos[0] - 5, image_pos[1] - 10, 10, 10), 2)

            # Draw the eye
            pygame.draw.circle(screen, WHITE, eye_pos, eye_size[0]//2)
            pygame.draw.circle(screen, BROWN, (eye_pos[0] - 5, eye_pos[1]), 10)

            # Rays and angles
            ray_points = [real_pos_smooth[1] - 10, real_pos_smooth[1] + candle_size[1]//2, real_pos_smooth[1] + candle_size[1]]
            for i, y in enumerate(ray_points):
                real_point = (real_pos_smooth[0], y)
                eye_point = (eye_pos[0], eye_pos[1])
                mirror_point = find_mirror_point_smooth(real_point, eye_point, mirror_x)

                pygame.draw.line(screen, RED, real_point, mirror_point, 2)
                draw_dashed_line(ray_surface, (*RED, RAY_OPACITY), mirror_point, eye_point)

                angle = calculate_angle_smooth(real_point, mirror_point, eye_point)
                label_prefix = "Angle of Incidence:" if i == 0 else "Angle of Reflection:"
                if label_prefix:
                    label = font.render(f"{label_prefix} {angle:.1f}°", True, BLACK)
                    screen.blit(label, (mirror_x + 10, mirror_point[1] - 10))

                reflected_direction = reflect_ray_outside_smooth(real_point, mirror_point, angle)
                reflected_end = (mirror_point[0] + reflected_direction[0] * 200, mirror_point[1] + reflected_direction[1] * 200)
                pygame.draw.line(ray_surface, (*RED, RAY_OPACITY), mirror_point, reflected_end, 2)

                if i == 0:
                    real_label = font.render(f"Real Point: ({int(real_point[0])}, {int(real_point[1])})", True, BLACK)
                    screen.blit(real_label, (real_point[0] - 50, real_point[1] - 30))
                    mirror_label = font.render(f"Mirror Point: ({int(mirror_point[0])}, {int(mirror_point[1])})", True, BLACK)
                    screen.blit(mirror_label, (mirror_point[0] + 10, mirror_point[1] + 20))
                    reflected_label = font.render(f"Reflected End: ({int(reflected_end[0])}, {int(reflected_end[1])})", True, BLACK)
                    screen.blit(reflected_label, (reflected_end[0] + 10, reflected_end[1] + 10))

            label = font.render("Inside of Mirror", True, BLACK)
            screen.blit(label, (mirror_x - label.get_width() - 10, HEIGHT - 30))

        else:  # Rough mode
            # Draw the rough surface
            for i in range(len(mirror_points) - 1):
                pygame.draw.line(screen, BLACK, mirror_points[i], mirror_points[i + 1], 4)

            # Draw the candle (real)
            pygame.draw.rect(screen, YELLOW, (real_pos_rough[0] - candle_size[0]//2, real_pos_rough[1], candle_size[0], candle_size[1]))
            pygame.draw.rect(screen, BLACK, (real_pos_rough[0] - 5, real_pos_rough[1] - 10, 10, 10))

            # Rays and angles
            num_rays = 10
            ray_spacing = 20
            for i in range(num_rays):
                start_x = real_pos_rough[0] - (num_rays * ray_spacing) / 2 + i * ray_spacing
                start_y = real_pos_rough[1] - 50
                real_point = (start_x, start_y)
                end_point = (start_x, HEIGHT)
                mirror_point_data = find_mirror_point_rough(real_point, end_point)
                if mirror_point_data is None:
                    continue
                mirror_point = (mirror_point_data[0], mirror_point_data[1])
                segment_index = mirror_point_data[2]

                pygame.draw.line(screen, YELLOW, real_point, mirror_point, 2)

                reflected_directions = reflect_ray_outside_rough(real_point, mirror_point, segment_index)
                for j, reflected_direction in enumerate(reflected_directions):
                    reflected_end = (mirror_point[0] + reflected_direction[0] * 200, mirror_point[1] + reflected_direction[1] * 200)
                    draw_dashed_line(ray_surface, (*YELLOW, RAY_OPACITY), mirror_point, reflected_end)

                    if i == 0:
                        angle_incident, angle_reflected = calculate_angle_rough(real_point, mirror_point, reflected_direction, segment_index)
                        if j == 0:
                            label = font.render(f"Angle of Incidence: {angle_incident:.1f}°", True, BLACK)
                            screen.blit(label, (mirror_point[0] - 150, mirror_point[1] - 30))
                        label = font.render(f"Angle of Reflection: {angle_reflected:.1f}°", True, BLACK)
                        screen.blit(label, (mirror_point[0] - 150, mirror_point[1] + j * 20 - 10))

            label = font.render("Rough Surface", True, BLACK)
            screen.blit(label, (WIDTH - 120, mirror_y + 10))

        # Blit the ray surface onto the main screen
        screen.blit(ray_surface, (0, 0))

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(1.0 / 60)

async def main():
    setup()
    await update_loop()

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())