import pygame
import math

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 900, 450
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Law of Reflection Simulation")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)       # For candle flame and rays
YELLOW = (255, 255, 0)  # For candle body
BROWN = (139, 69, 19)   # For eye pupil
GRAY = (127, 127, 127)
LIGHT_BLUE = (173, 216, 230)  # Background color from image

# Font
font = pygame.font.SysFont("arial", 16, bold=True)

# Initial positions (adjusted to match the image)
mirror_x = 450
real_pos = [750, 280]  # Candle position
image_pos = [150, 280]  # Virtual image position
eye_pos = [800, 80]    # Eye position
candle_size = (20, 60)  # Width, height of candle
eye_size = (40, 40)     # Eye diameter

# Dragging state
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
    # Find where the line from start to end intersects the mirror (x = mirror_x)
    x1, y1 = start
    x2, y2 = end
    if x2 == x1:  # Avoid division by zero
        return (mirror_x, y1)
    t = (mirror_x - x1) / (x2 - x1)
    y = y1 + t * (y2 - y1)
    return (mirror_x, y)

def calculate_angle(incident_point, mirror_point, reflected_point):
    # Normal is horizontal (along x-axis) for a vertical mirror
    normal = (1, 0)  # Normal vector (pointing left)

    # Incident ray vector (from candle to mirror point)
    incident = (mirror_point[0] - incident_point[0], mirror_point[1] - incident_point[1])
    incident_magnitude = math.sqrt(incident[0]**2 + incident[1]**2)
    if incident_magnitude == 0:
        return 0
    incident = (incident[0] / incident_magnitude, incident[1] / incident_magnitude)

    # Dot product to find angle between incident ray and normal
    dot_product = incident[0] * normal[0] + incident[1] * normal[1]
    angle = math.degrees(math.acos(abs(dot_product)))

    return angle

def main():
    global dragging, offset_x, offset_y, real_pos, image_pos, eye_pos
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                # Dragging candle
                if (real_pos[0] - candle_size[0]//2 <= mouse_pos[0] <= real_pos[0] + candle_size[0]//2 and
                    real_pos[1] <= mouse_pos[1] <= real_pos[1] + candle_size[1]):
                    dragging = "real"
                    offset_x = mouse_pos[0] - real_pos[0]
                    offset_y = mouse_pos[1] - real_pos[1]
                # Dragging virtual image
                elif (image_pos[0] - candle_size[0]//2 <= mouse_pos[0] <= image_pos[0] + candle_size[0]//2 and
                      image_pos[1] <= mouse_pos[1] <= image_pos[1] + candle_size[1]):
                    dragging = "image"
                    offset_x = mouse_pos[0] - image_pos[0]
                    offset_y = mouse_pos[1] - image_pos[1]
                # Dragging eye
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

        # Clear screen
        screen.fill(LIGHT_BLUE)

        # Draw mirror
        pygame.draw.line(screen, BLACK, (mirror_x, 0), (mirror_x, HEIGHT), 4)

        # Draw real candle
        pygame.draw.rect(screen, YELLOW, (real_pos[0] - candle_size[0]//2, real_pos[1], candle_size[0], candle_size[1]))
        pygame.draw.rect(screen, RED, (real_pos[0] - 5, real_pos[1] - 10, 10, 10))  # Flame

        # Draw virtual image
        pygame.draw.rect(screen, YELLOW, (image_pos[0] - candle_size[0]//2, image_pos[1], candle_size[0], candle_size[1]), 2)
        pygame.draw.rect(screen, RED, (image_pos[0] - 5, image_pos[1] - 10, 10, 10), 2)  # Flame outline

        # Draw eye
        pygame.draw.circle(screen, WHITE, eye_pos, eye_size[0]//2)
        pupil_pos = (eye_pos[0] - 5, eye_pos[1])  # Simplified pupil
        pygame.draw.circle(screen, BROWN, pupil_pos, 10)

        # Draw rays (3 rays: top, middle, bottom of candle)
        ray_points = [
            (real_pos[1] - 10),  # Top (flame)
            (real_pos[1] + candle_size[1]//2),  # Middle
            (real_pos[1] + candle_size[1])  # Bottom
        ]
        for i, y in enumerate(ray_points):
            real_point = (real_pos[0], y)
            eye_point = (eye_pos[0], eye_pos[1])

            # Find the mirror point where the ray from real_point to eye_point hits the mirror
            mirror_point = find_mirror_point(real_point, eye_point, mirror_x)

            # Incident ray (candle to mirror)
            pygame.draw.line(screen, RED, real_point, mirror_point, 2)

            # Reflected ray (mirror to eye, dashed)
            draw_dashed_line(screen, RED, mirror_point, eye_point)

            # Calculate and display angle
            angle = calculate_angle(real_point, mirror_point, eye_point)
            angle_text = font.render(f"{angle:.1f}°", True, BLACK)
            screen.blit(angle_text, (mirror_x + 10, mirror_point[1] - 10 if i == 0 else mirror_point[1] + 10))

        # Draw "Inside of Mirror" label
        label = font.render("Inside of Mirror", True, BLACK)
        screen.blit(label, (mirror_x - label.get_width() - 10, HEIGHT - 30))

        # Update display
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()