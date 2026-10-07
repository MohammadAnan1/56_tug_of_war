import pygame


class Puller:
    """Represents a puller character anchor on either side of the rope."""

    def __init__(self, x, y, color, label):
        self.x = x
        self.y = y
        self.color = color
        self.label = label
        self.font = pygame.font.SysFont(None, 24)

        # Dynamic leaning amount
        self.lean = 0.0

    def render(self, surface):
        """Draw avatar with dynamic leaning."""

        lean = int(self.lean)

        # Body becomes slightly slanted based on lean direction
        body_points = [
            (self.x - 20, self.y - 35),
            (self.x + 20, self.y - 35),
            (self.x + 20 + lean, self.y + 35),
            (self.x - 20 + lean, self.y + 35)
        ]

        pygame.draw.polygon(
            surface,
            self.color,
            body_points
        )

        # Head follows the leaning direction
        head_x = self.x + int(lean * 1.2)

        pygame.draw.circle(
            surface,
            (240, 210, 180),
            (head_x, self.y - 50),
            16
        )

        # Name / control tag
        label_surf = self.font.render(
            self.label,
            True,
            (240, 240, 240)
        )

        surface.blit(
            label_surf,
            (
                self.x - label_surf.get_width() // 2,
                self.y + 45
            )
        )