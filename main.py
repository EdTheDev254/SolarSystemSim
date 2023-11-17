import pygame
import sys
import math
import random

# Set up Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
FPS = 60
G = 1  # Gravitational constant

# Create a Pygame window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Planet and Star Simulation")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

# Define a celestial body class
class CelestialBody:
    def __init__(self, mass, radius, position, velocity, color):
        self.mass = mass
        self.radius = radius
        self.position = position
        self.velocity = velocity
        self.color = color

# Initial conditions for the star and planet
star = CelestialBody(mass=10000, radius=20, position=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), velocity=(0, 0), color=YELLOW)

# Fast planet for template velocity
fast_planet = CelestialBody(mass=100, radius=10, position=(SCREEN_WIDTH // 2 + 150, SCREEN_HEIGHT // 2), velocity=(0, -2), color=WHITE)

# List to store planet instances
planets = []

# Timestep for the simulation
dt = 0.1

# Flag to indicate if the planet is being dragged
dragging_planet = False
dragged_planet = None
offset_x, offset_y = 0, 0

# Dictionary to store the positions of the planet for the orbit line
orbit_lines = {}

# Function to set initial velocity based on a template planet
def set_initial_velocity_based_on_template(planet, template):
    scaling_factor = 2  # Adjust this factor to control the speed of the new planets
    planet.velocity = (template.velocity[0] * scaling_factor, template.velocity[1] * scaling_factor)

# Function to generate random mass and color for a new planet
def generate_random_mass_and_color():
    random_mass = random.uniform(50, 200)  # Adjust the mass range as needed
    random_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    return random_mass, random_color

# Function to check if a planet is within the window boundaries
def is_planet_within_window(planet):
    return 0 <= planet.position[0] <= SCREEN_WIDTH and 0 <= planet.position[1] <= SCREEN_HEIGHT

# Main game loop
running = True
while running:
    time_delta = pygame.time.Clock().tick(FPS) / 1000.0

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                # Check if the mouse click is on a planet
                clicked_planet = None
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for planet in planets:
                    planet_rect = pygame.Rect(planet.position[0] - planet.radius, planet.position[1] - planet.radius,
                                              2 * planet.radius, 2 * planet.radius)
                    if planet_rect.collidepoint(mouse_x, mouse_y):
                        clicked_planet = planet
                        dragging_planet = True
                        dragged_planet = clicked_planet
                        offset_x = clicked_planet.position[0] - mouse_x
                        offset_y = clicked_planet.position[1] - mouse_y
                        # Clear the orbit line when dragging starts
                        orbit_lines[clicked_planet] = []
                        break

                if clicked_planet is None:
                    # Create a new planet instance at the clicked position
                    random_mass, random_color = generate_random_mass_and_color()
                    new_planet = CelestialBody(mass=random_mass, radius=10, position=(mouse_x, mouse_y), velocity=(0, 0), color=random_color)
                    set_initial_velocity_based_on_template(new_planet, fast_planet)
                    planets.append(new_planet)
                    dragging_planet = True
                    dragged_planet = new_planet
                    orbit_lines[new_planet] = []  # Create a new orbit line list for the new planet

            elif event.button == 3:  # Right mouse button
                # Check if the mouse click is on a planet
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for planet in planets:
                    planet_rect = pygame.Rect(planet.position[0] - planet.radius, planet.position[1] - planet.radius,
                                              2 * planet.radius, 2 * planet.radius)
                    if planet_rect.collidepoint(mouse_x, mouse_y):
                        # Remove the planet and its corresponding orbit line
                        planets.remove(planet)
                        del orbit_lines[planet]

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                dragging_planet = False
                dragged_planet = None

    # Gravity simulation for each planet
    for planet in planets:
        distance = math.sqrt((planet.position[0] - star.position[0]) ** 2 + (planet.position[1] - star.position[1]) ** 2)
        acceleration = G * star.mass / distance ** 2

        dx = (star.position[0] - planet.position[0]) / distance
        dy = (star.position[1] - planet.position[1]) / distance

        planet.velocity = (planet.velocity[0] + acceleration * dx * dt, planet.velocity[1] + acceleration * dy * dt)

        if not dragging_planet or (dragging_planet and planet != dragged_planet):
            planet.position = (planet.position[0] + planet.velocity[0] * dt, planet.position[1] + planet.velocity[1] * dt)

        orbit_lines[planet].append((int(planet.position[0]), int(planet.position[1])))

        # Check if the planet is still within the window boundaries
        if not is_planet_within_window(planet):
            planets.remove(planet)
            del orbit_lines[planet]

    # If dragging a planet, update its position and clear the orbit line
    if dragging_planet and dragged_planet is not None:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dragged_planet.position = (mouse_x + offset_x, mouse_y + offset_y)
        orbit_lines[dragged_planet] = []

    # Draw background
    screen.fill(BLACK)

    # Draw star
    pygame.draw.circle(screen, star.color, (int(star.position[0]), int(star.position[1])), star.radius)

    # Draw planets and their orbit lines
    for planet, orbit_line in orbit_lines.items():
        pygame.draw.circle(screen, planet.color, (int(planet.position[0]), int(planet.position[1])), planet.radius)

        # Draw orbit line for the planet
        for i in range(len(orbit_line) - 1):
            alpha_value = int(255 * (1 - i / len(orbit_line)))
            pygame.draw.line(screen, (255, 255, 255, alpha_value), orbit_line[i], orbit_line[i + 1], 1)

    # Update display
    pygame.display.flip()
    
# Quit Pygame
pygame.quit()
sys.exit()
