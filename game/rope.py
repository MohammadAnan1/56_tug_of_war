import math
import pygame


class Rope:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.center_y = screen_height // 2
        self.marker_x = float(screen_width // 2)

        self.left_win_x = 180
        self.right_win_x = screen_width - 180
        self.pull_step = 12

        # Used for rope tension/animation
        self.velocity = 0.0
        self.tension = 0.0

    def pull_left(self, strength=1.0):
        amount = self.pull_step * strength
        self.marker_x -= amount
        self.velocity = -strength

    def pull_right(self, strength=1.0):
        amount = self.pull_step * strength
        self.marker_x += amount
        self.velocity = strength

    def update(self):
        # Gradually reduce pulling momentum
        self.velocity *= 0.90

        # Tension is based on current pulling momentum
        self.tension = min(abs(self.velocity), 2.0)

    def check_winner(self):
        if self.marker_x <= self.left_win_x:
            return "PLAYER"

        if self.marker_x >= self.right_win_x:
            return "COMPUTER"

        return None

    def reset(self):
        self.marker_x = float(self.screen_width // 2)
        self.velocity = 0.0
        self.tension = 0.0

    def render(self, surface):
        # Calculate rope animation
        tension = min(self.tension / 2.0, 1.0)

        vibration = 2 + (6 * tension)
        sag = 3 + (10 * tension)

        points = []

        start_x = 60
        end_x = self.screen_width - 60

        segments = 40

        for i in range(segments + 1):
            x = start_x + (end_x - start_x) * i / segments

            # Normal rope shape
            y = self.center_y

            # Sag is strongest near the center
            center_factor = 1 - abs(
                (x - self.screen_width / 2)
                / (self.screen_width / 2)
            )

            y += sag * center_factor

            # Vibration increases with tension
            y += math.sin(i * 1.8 + pygame.time.get_ticks() * 0.025) * vibration

            points.append((int(x), int(y)))

        pygame.draw.lines(
            surface,
            (180, 140, 90),
            False,
            points,
            10
        )

        # Left winning boundary
        pygame.draw.line(
            surface,
            (50, 200, 50),
            (self.left_win_x, self.center_y - 40),
            (self.left_win_x, self.center_y + 40),
            4
        )

        # Right winning boundary
        pygame.draw.line(
            surface,
            (200, 50, 50),
            (self.right_win_x, self.center_y - 40),
            (self.right_win_x, self.center_y + 40),
            4
        )

        # Center boundary
        pygame.draw.line(
            surface,
            (120, 120, 120),
            (self.screen_width // 2, self.center_y - 20),
            (self.screen_width // 2, self.center_y + 20),
            2
        )

        # Center flag
        flag_rect = pygame.Rect(
            int(self.marker_x) - 12,
            self.center_y - 24,
            24,
            48
        )

        pygame.draw.rect(
            surface,
            (230, 40, 40),
            flag_rect,
            border_radius=4
        )

        pygame.draw.rect(
            surface,
            (255, 255, 255),
            flag_rect,
            width=2,
            border_radius=4
        )