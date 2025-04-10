import pygame
import math

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 900, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Law of Reflection Simulation with Grid")

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
material_button_rects = []
slider_x = 150
slider_width = 200

# Object positions
mirror_x = 450
real_pos = [750, 280]
image_pos = [150, 280]
eye_pos = [800, 80]
candle_size = (20, 60)
eye_size = (40, 40)

dragging = None
offset_x, offset_y = 0, 0

# Grid settings
GRID_SIZE = 50  # Grid spacing in pixels

def draw_grid():
    # Draw vertical grid lines (x-axis)
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, LIGHT_GRAY, (x, 0), (x, HEIGHT), 1)
        # Label x-axis
        label = font.render(str(x), True, BLACK)
        screen.blit(label, (x, HEIGHT - 20))

    # Draw horizontal grid lines (y-axis)
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, LIGHT_GRAY, (0, y), (WIDTH, y), 1)
        # Label y-axis
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

def find_mirror_point(start, end, mirror_x):
    x1, y1 = start
    x2, y2 = end
    if x2 == x1:
        return (mirror_x, y1)
    t = (mirror_x - x1) / (x2 - x1)
    y = y1 + t * (y2 - y1)
    return (mirror_x, y)

def calculate_angle(incident_point, mirror_point, reflected_point):
    normal = (1, 0)  # The normal vector is horizontal, since the mirror is vertical
    incident = (mirror_point[0] - incident_point[0], mirror_point[1] - incident_point[1])
    incident_magnitude = math.sqrt(incident[0]**2 + incident[1]**2)
    if incident_magnitude == 0:
        return 0
    incident = (incident[0] / incident_magnitude, incident[1] / incident_magnitude)
    dot_product = incident[0] * normal[0] + incident[1] * normal[1]
    angle = math.degrees(math.acos(abs(dot_product)))
    return angle

def reflect_ray_outside(incident_point, mirror_point, angle_of_incidence):
    normal = (1, 0)  # Normal to the mirror, which is vertical (pointing to the right)
    incident = (mirror_point[0] - incident_point[0], mirror_point[1] - incident_point[1])
    incident_magnitude = math.sqrt(incident[0]**2 + incident[1]**2)
    if incident_magnitude == 0:
        return (0, 0)
    incident = (incident[0] / incident_magnitude, incident[1] / incident_magnitude)

    # Compute the reflected vector: R = I - 2(I·N)N
    dot_product = incident[0] * normal[0] + incident[1] * normal[1]
    reflected = (
        incident[0] - 2 * dot_product * normal[0],
        incident[1] - 2 * dot_product * normal[1]
    )
    return reflected

def main():
    global dragging, offset_x, offset_y, real_pos, image_pos, eye_pos
    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill(LIGHT_BLUE)

        # Draw the grid
        draw_grid()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if (real_pos[0] - candle_size[0]//2 <= mouse_pos[0] <= real_pos[0] + candle_size[0]//2 and
                    real_pos[1] <= mouse_pos[1] <= real_pos[1] + candle_size[1]):
                    dragging = "real"
                    offset_x = mouse_pos[0] - real_pos[0]
                    offset_y = mouse_pos[1] - real_pos[1]
                elif (image_pos[0] - candle_size[0]//2 <= mouse_pos[0] <= image_pos[0] + candle_size[0]//2 and
                      image_pos[1] <= mouse_pos[1] <= image_pos[1] + candle_size[1]):
                    dragging = "image"
                    offset_x = mouse_pos[0] - image_pos[0]
                    offset_y = mouse_pos[1] - real_pos[1]
                elif (eye_pos[0] - eye_size[0]//2 <= mouse_pos[0] <= eye_pos[0] + eye_size[0]//2 and
                      eye_pos[1] - eye_size[1]//2 <= mouse_pos[1] <= eye_pos[1] + eye_size[1]//2):
                    dragging = "eye"
                    offset_x = mouse_pos[0] - eye_pos[0]
                    offset_y = mouse_pos[1] - eye_pos[1]

            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = None
            elif event.type == pygame.MOUSEMOTION and dragging:
                mouse_pos = pygame.mouse.get_pos()
                if dragging == "real":
                    real_pos[0] = max(mirror_x + 50, min(850, mouse_pos[0] - offset_x))
                    real_pos[1] = max(0, min(HEIGHT - 100, mouse_pos[1] - offset_y))
                    image_pos[0] = mirror_x - (real_pos[0] - mirror_x)
                    image_pos[1] = real_pos[1]
                elif dragging == "image":
                    image_pos[0] = max(50, min(mirror_x - 50, mouse_pos[0] - offset_x))
                    image_pos[1] = max(0, min(HEIGHT - 100, mouse_pos[1] - offset_y))
                    real_pos[0] = mirror_x + (mirror_x - image_pos[0])
                    real_pos[1] = image_pos[1]
                elif dragging == "eye":
                    eye_pos[0] = max(mirror_x + 50, min(850, mouse_pos[0] - offset_x))
                    eye_pos[1] = max(50, min(HEIGHT - 50, mouse_pos[1] - offset_y))

        # Draw the mirror
        pygame.draw.line(screen, BLACK, (mirror_x, 0), (mirror_x, HEIGHT), 4)

        # Draw the candle (real and image)
        pygame.draw.rect(screen, YELLOW, (real_pos[0] - candle_size[0]//2, real_pos[1], candle_size[0], candle_size[1]))
        pygame.draw.rect(screen, RED, (real_pos[0] - 5, real_pos[1] - 10, 10, 10))

        pygame.draw.rect(screen, YELLOW, (image_pos[0] - candle_size[0]//2, image_pos[1], candle_size[0], candle_size[1]), 2)
        pygame.draw.rect(screen, RED, (image_pos[0] - 5, image_pos[1] - 10, 10, 10), 2)

        # Draw the eye
        pygame.draw.circle(screen, WHITE, eye_pos, eye_size[0]//2)
        pygame.draw.circle(screen, BROWN, (eye_pos[0] - 5, eye_pos[1]), 10)

        # Rays and angles
        ray_points = [real_pos[1] - 10, real_pos[1] + candle_size[1]//2, real_pos[1] + candle_size[1]]
        for i, y in enumerate(ray_points):
            real_point = (real_pos[0], y)
            eye_point = (eye_pos[0], eye_pos[1])
            mirror_point = find_mirror_point(real_point, eye_point, mirror_x)

            # Draw the incident ray (from real point to mirror point)
            pygame.draw.line(screen, RED, real_point, mirror_point, 2)

            # Draw the reflected ray to the eye (dashed line from mirror point to eye)
            draw_dashed_line(screen, RED, mirror_point, eye_point)

            # Calculate the angle of incidence
            angle = calculate_angle(real_point, mirror_point, eye_point)
            label_prefix = "Angle of Incidence:" if i == 0 else "Angle of Reflection:"
            if label_prefix:
                label = font.render(f"{label_prefix} {angle:.1f}°", True, BLACK)
                screen.blit(label, (mirror_x + 10, mirror_point[1] - 10))

            # Reflect the ray outside the mirror (on the same side as the incident ray)
            reflected_direction = reflect_ray_outside(real_point, mirror_point, angle)
            reflected_end = (
                mirror_point[0] + reflected_direction[0] * 200,
                mirror_point[1] + reflected_direction[1] * 200
            )
            pygame.draw.line(screen, RED, mirror_point, reflected_end, 2)

            # Display coordinates for manual calculation
            if i == 0:  # Only display for the first ray to avoid clutter
                # Real point coordinates
                real_label = font.render(f"Real Point: ({int(real_point[0])}, {int(real_point[1])})", True, BLACK)
                screen.blit(real_label, (real_point[0] - 50, real_point[1] - 30))

                # Mirror point coordinates
                mirror_label = font.render(f"Mirror Point: ({int(mirror_point[0])}, {int(mirror_point[1])})", True, BLACK)
                screen.blit(mirror_label, (mirror_point[0] + 10, mirror_point[1] + 20))

                # Reflected end coordinates
                reflected_label = font.render(f"Reflected End: ({int(reflected_end[0])}, {int(reflected_end[1])})", True, BLACK)
                screen.blit(reflected_label, (reflected_end[0] + 10, reflected_end[1] + 10))

        label = font.render("Inside of Mirror", True, BLACK)
        screen.blit(label, (mirror_x - label.get_width() - 10, HEIGHT - 30))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()