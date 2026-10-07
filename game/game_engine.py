import random
import pygame
from game.rope import Rope
from game.player import Puller


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.rope = Rope(width, height)

        self.player = Puller(
            90,
            height // 2,
            (50, 120, 220),
            "PLAYER (A/D)"
        )

        self.computer = Puller(
            width - 90,
            height // 2,
            (220, 80, 50),
            "COMPUTER"
        )

        # Input state
        self.last_key = None

        # Game state
        self.winner = None
        self.game_state = "PLAYING"

        # AI
        self.normal_computer_cooldown = 180
        self.panic_computer_cooldown = 90
        self.last_computer_pull = pygame.time.get_ticks()

        # Panic mode
        self.panic_mode = False
        self.panic_threshold = self.rope.left_win_x + 140

        # Match timer
        self.match_start_time = pygame.time.get_ticks()
        self.match_duration = 45

        # Sudden Death
        self.sudden_death = False

        # Fonts
        self.font_big = pygame.font.SysFont(None, 48)
        self.font_small = pygame.font.SysFont(None, 26)
        self.font_timer = pygame.font.SysFont(None, 32)

    def handle_event(self, event):
        # Handle restart after Game Over
        if self.game_state != "PLAYING":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
            return

        # Player input
        if event.type == pygame.KEYDOWN:

            if event.key in (pygame.K_a, pygame.K_d):

                # Only ignore the same key.
                # This fixes the A/D deadlock caused by the old lock system.
                if event.key != self.last_key:

                    pull_strength = 1.0

                    # Sudden Death doubles player pulling power
                    if self.sudden_death:
                        pull_strength *= 2.0

                    self.rope.pull_left(pull_strength)

                    self.last_key = event.key

    def update(self):
        if self.game_state != "PLAYING":
            return

        now = pygame.time.get_ticks()

        # -----------------------------------
        # MATCH TIMER
        # -----------------------------------

        elapsed_seconds = (now - self.match_start_time) / 1000

        # Activate Sudden Death after 45 seconds
        if elapsed_seconds >= self.match_duration:
            self.sudden_death = True

        # -----------------------------------
        # ROPE ANIMATION
        # -----------------------------------

        self.rope.update()

        # -----------------------------------
        # AI PANIC MODE
        # -----------------------------------

        # Player wins on the left.
        # Therefore, when marker gets close to left boundary,
        # computer enters panic mode.
        if self.rope.marker_x <= self.panic_threshold:
            self.panic_mode = True
        else:
            self.panic_mode = False

        # Choose AI reaction interval
        if self.panic_mode:
            computer_cooldown = self.panic_computer_cooldown
        else:
            computer_cooldown = self.normal_computer_cooldown

        # -----------------------------------
        # COMPUTER PULL
        # -----------------------------------

        if now - self.last_computer_pull >= computer_cooldown:

            computer_strength = random.uniform(0.7, 1.2)

            # Panic mode makes computer stronger
            if self.panic_mode:
                computer_strength *= 1.6

            # Sudden Death doubles pulling power
            if self.sudden_death:
                computer_strength *= 2.0

            self.rope.pull_right(computer_strength)

            self.last_computer_pull = now

        # -----------------------------------
        # CHARACTER LEANING
        # -----------------------------------

        # Negative velocity = player pulling left
        # Positive velocity = computer pulling right
        momentum = self.rope.velocity

        if momentum < 0:
            lean_amount = min(abs(momentum) * 12, 18)

            self.player.lean = -lean_amount
            self.computer.lean = -lean_amount * 0.35

        elif momentum > 0:
            lean_amount = min(abs(momentum) * 12, 18)

            self.player.lean = lean_amount * 0.35
            self.computer.lean = lean_amount

        else:
            # Gradually return characters toward neutral
            self.player.lean *= 0.9
            self.computer.lean *= 0.9

        # -----------------------------------
        # WINNER CHECK
        # -----------------------------------

        result = self.rope.check_winner()

        if result:
            self.winner = result
            self.game_state = "GAME_OVER"

    def reset(self):
        self.rope.reset()

        # Reset input
        self.last_key = None

        # Reset game state
        self.winner = None
        self.game_state = "PLAYING"

        # Reset AI
        self.panic_mode = False
        self.last_computer_pull = pygame.time.get_ticks()

        # Reset timer
        self.match_start_time = pygame.time.get_ticks()

        # Reset Sudden Death
        self.sudden_death = False

        # Reset character leaning
        self.player.lean = 0
        self.computer.lean = 0

    def render(self, screen):
        screen.fill((30, 32, 36))

        # Background mud area
        mud_rect = pygame.Rect(
            self.width // 2 - 120,
            self.height // 2 - 80,
            240,
            160
        )

        pygame.draw.rect(
            screen,
            (45, 38, 30),
            mud_rect,
            border_radius=12
        )

        # Rope
        self.rope.render(screen)

        # Pullers
        self.player.render(screen)
        self.computer.render(screen)

        # -----------------------------------
        # TIMER
        # -----------------------------------

        now = pygame.time.get_ticks()
        elapsed_seconds = int(
            (now - self.match_start_time) / 1000
        )

        timer_text = f"TIME: {elapsed_seconds}s"

        timer_surf = self.font_timer.render(
            timer_text,
            True,
            (240, 240, 240)
        )

        screen.blit(
            timer_surf,
            (
                self.width // 2 - timer_surf.get_width() // 2,
                8
            )
        )

        # -----------------------------------
        # SUDDEN DEATH DISPLAY
        # -----------------------------------

        if self.sudden_death and self.game_state == "PLAYING":

            sudden_surf = self.font_small.render(
                "SUDDEN DEATH!  PULLING POWER x2",
                True,
                (255, 220, 80)
            )

            screen.blit(
                sudden_surf,
                (
                    self.width // 2 - sudden_surf.get_width() // 2,
                    38
                )
            )

        else:

            inst_surf = self.font_small.render(
                "Alternate [A] and [D] keys rapidly to pull!",
                True,
                (210, 210, 210)
            )

            screen.blit(
                inst_surf,
                (
                    self.width // 2 - inst_surf.get_width() // 2,
                    40
                )
            )

        # -----------------------------------
        # PANIC MODE DISPLAY
        # -----------------------------------

        if self.panic_mode and self.game_state == "PLAYING":

            panic_surf = self.font_small.render(
                "COMPUTER PANIC!",
                True,
                (255, 120, 80)
            )

            screen.blit(
                panic_surf,
                (
                    self.width // 2 - panic_surf.get_width() // 2,
                    68
                )
            )

        # -----------------------------------
        # GAME OVER
        # -----------------------------------

        if self.game_state == "GAME_OVER":

            overlay = pygame.Surface(
                (self.width, self.height),
                pygame.SRCALPHA
            )

            overlay.fill((0, 0, 0, 180))

            screen.blit(
                overlay,
                (0, 0)
            )

            win_text = f"{self.winner} WINS!"

            color = (
                (80, 220, 80)
                if self.winner == "PLAYER"
                else (240, 80, 80)
            )

            text_surf = self.font_big.render(
                win_text,
                True,
                color
            )

            screen.blit(
                text_surf,
                (
                    self.width // 2 - text_surf.get_width() // 2,
                    self.height // 2 - 50
                )
            )

            restart_surf = self.font_small.render(
                "Press [R] to Play Again",
                True,
                (240, 240, 240)
            )

            screen.blit(
                restart_surf,
                (
                    self.width // 2 - restart_surf.get_width() // 2,
                    self.height // 2 + 10
                )
            )