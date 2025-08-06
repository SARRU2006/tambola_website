import asyncio
import random
import platform
import pygame
import pygame.font
import pyttsx3
from num2words import num2words

# Text-to-speech setup
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)  # Set speaking rate

def speak_number(number):
    if number is not None:
        spoken = num2words(number)
        tts_engine.say(spoken)
        tts_engine.runAndWait()

# Game logic class
class TambolaGame:
    def _init_(self, num_tickets=6):
        self.num_tickets = num_tickets
        self.tickets = []
        self.available_numbers = list(range(1, 91))
        self.called_numbers = []
        self.current_number = None
        self.generate_tickets()

    def generate_tickets(self):
        self.tickets = []
        for _ in range(self.num_tickets):
            ticket = self._generate_single_ticket()
            self.tickets.append(ticket)

    def _generate_single_ticket(self):
        ticket = [[None for _ in range(3)] for _ in range(9)]
        col_ranges = [(1, 10), (11, 20), (21, 30), (31, 40), (41, 50),
                      (51, 60), (61, 70), (71, 80), (81, 90)]

        used_numbers = {i: [] for i in range(9)}

        for row in range(3):
            cols = random.sample(range(9), 5)
            for col in cols:
                start, end = col_ranges[col]
                while True:
                    num = random.randint(start, end)
                    if num not in used_numbers[col]:
                        used_numbers[col].append(num)
                        ticket[col][row] = num
                        break

        return ticket

    def pick_number(self):
        if self.available_numbers:
            self.current_number = random.choice(self.available_numbers)
            self.available_numbers.remove(self.current_number)
            self.called_numbers.append(self.current_number)
            return self.current_number
        return None

    def get_called_numbers(self):
        return self.called_numbers

# Pygame setup and UI
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tambola Game")
font = pygame.font.SysFont("arial", 24)
large_font = pygame.font.SysFont("arial", 48)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Animation variables
ticket_alpha = 0
ALPHA_STEP = 5
number_scale = 0.0
NUMBER_SCALE_DURATION = 30
number_scale_frame = 0

# Game state
game = TambolaGame(num_tickets=6)
generate_button = pygame.Rect(50, 500, 150, 50)
pick_button = pygame.Rect(250, 500, 150, 50)
win_animation = False
win_frame = 0

def setup():
    global ticket_alpha, number_scale, number_scale_frame, win_animation, win_frame
    ticket_alpha = 0
    number_scale = 0.0
    number_scale_frame = 0
    win_animation = False
    win_frame = 0
    game.generate_tickets()

def render():
    global ticket_alpha, number_scale, number_scale_frame, win_animation, win_frame
    screen.fill(WHITE)

    ticket_width = 300
    ticket_height = 100
    for t, ticket in enumerate(game.tickets):
        x_offset = 50 + (t % 2) * (ticket_width + 20)
        y_offset = 50 + (t // 2) * (ticket_height + 20)
        surface = pygame.Surface((ticket_width, ticket_height), pygame.SRCALPHA)
        surface.fill((255, 255, 255, ticket_alpha))

        cell_width = ticket_width // 9
        cell_height = ticket_height // 3
        for col in range(9):
            for row in range(3):
                rect = pygame.Rect(col * cell_width, row * cell_height, cell_width, cell_height)
                pygame.draw.rect(surface, BLACK, rect, 1)
                if ticket[col][row] is not None:
                    text = font.render(str(ticket[col][row]), True, BLACK)
                    text_rect = text.get_rect(center=(rect.centerx, rect.centery))
                    surface.blit(text, text_rect)

        if win_animation:
            border_color = RED if win_frame % 20 < 10 else BLUE
            pygame.draw.rect(surface, border_color, surface.get_rect(), 5)

        screen.blit(surface, (x_offset, y_offset))

    if ticket_alpha < 255:
        ticket_alpha = min(255, ticket_alpha + ALPHA_STEP)

    if game.current_number:
        scale = number_scale if number_scale > 0 else 1.0
        text = large_font.render(str(game.current_number), True, RED)
        scaled_text = pygame.transform.scale(text, (int(text.get_width() * scale), int(text.get_height() * scale)))
        text_rect = scaled_text.get_rect(center=(WIDTH - 100, 100))
        screen.blit(scaled_text, text_rect)
        if number_scale_frame < NUMBER_SCALE_DURATION:
            number_scale = 1.0 + (number_scale_frame / NUMBER_SCALE_DURATION)
            number_scale_frame += 1

    history = game.get_called_numbers()
    for i, num in enumerate(history[-5:]):
        text = font.render(str(num), True, BLACK)
        screen.blit(text, (WIDTH - 100, 150 + i * 30))

    pygame.draw.rect(screen, GRAY, generate_button)
    pygame.draw.rect(screen, GRAY, pick_button)
    screen.blit(font.render("New Tickets", True, BLACK), (generate_button.x + 10, generate_button.y + 15))
    screen.blit(font.render("Pick Number", True, BLACK), (pick_button.x + 10, pick_button.y + 15))

    pygame.display.flip()

def handle_events():
    global win_animation, win_frame, number_scale, number_scale_frame
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if generate_button.collidepoint(event.pos):
                setup()
            if pick_button.collidepoint(event.pos):
                number = game.pick_number()
                number_scale = 0.0
                number_scale_frame = 0
                speak_number(number)  # Announce the number aloud
                if random.random() < 0.1:
                    win_animation = True
                    win_frame = 0
    return True

def update_loop():
    global win_frame, win_animation
    if win_animation:
        win_frame += 1
        if win_frame > 60:
            win_animation = False

async def main():
    setup()
    running = True
    while running:
        running = handle_events()
        update_loop()
        render()
        await asyncio.sleep(1.0 / 60)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if _name_ == "_main_":
        asyncio.run(main())
