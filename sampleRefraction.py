import pygame
import math

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 900, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Law of Reflection Simulation with Materials")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
GRAY = (200, 200, 200)
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


def reflect_ray(incident_point, mirror_point, angle_of_incidence):
    # Calculate the reflection direction from the point of incidence
    normal = (1, 0)  # Normal to the mirror, which is vertical
    incident = (mirror_point[0] - incident_point[0], mirror_point[1] - incident_point[1])
    incident_magnitude = math.sqrt(incident[0]**2 + incident[1]**2)
    if incident_magnitude == 0:
        return (0, 0)
    incident = (incident[0] / incident_magnitude, incident[1] / incident_magnitude)

    # Reflection vector: The angle of incidence equals the angle of reflection
    reflected = (incident[0], -incident[1])  # Flip the y-component for reflection
    return reflected


def draw_grid(surface):
    # Draw a grid
    grid_size = 50
    for x in range(0, WIDTH, grid_size):
        pygame.draw.line(surface, GRAY, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, grid_size):
        pygame.draw.line(surface, GRAY, (0, y), (WIDTH, y), 1)


def main():
    global dragging, offset_x, offset_y, real_pos, image_pos, eye_pos, selected_material_index, custom_n
    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill(LIGHT_BLUE)

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
                    offset_y = mouse_pos[1] - image_pos[1]
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

        # Draw the grid
        draw_grid(screen)

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
            pygame.draw.line(screen, RED, real_point, mirror_point, 2)
            draw_dashed_line(screen, RED, mirror_point, eye_point)

            # Calculate the angle of incidence and reflection based on the mirror interaction
            angle = calculate_angle(real_point, mirror_point, eye_point)
            label_prefix = "Angle of Incidence:" if i == 0 else "Angle of Reflection:"
            if label_prefix:
                label = font.render(f"{label_prefix} {angle:.1f}°", True, BLACK)
                screen.blit(label, (mirror_x + 10, mirror_point[1] - 10))

            # Reflect the ray inside the screen's visible area
            reflected_ray = reflect_ray(real_point, mirror_point, angle)
            pygame.draw.line(screen, RED, mirror_point, reflected_ray)

        # Display current cursor position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        pos_text = font.render(f"Cursor: ({mouse_x}, {mouse_y})", True, BLACK)
        screen.blit(pos_text, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
