import pygame
import random

pygame.init()

# Window
WIDTH = 600
HEIGHT = 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

# Colors
black = (0,0,0)
green = (0,255,0)
red = (255,0,0)
white = (255,255,255)

clock = pygame.time.Clock()

snake_block = 10
snake_speed = 15

font = pygame.font.SysFont(None, 35)

def draw_snake(block, snake_list):
    for x in snake_list:
        pygame.draw.rect(screen, green, [x[0], x[1], block, block])

def message(msg, color):
    mesg = font.render(msg, True, color)
    screen.blit(mesg, [WIDTH/6, HEIGHT/3])

def game():
    game_over = False
    game_close = False

    x = WIDTH/2
    y = HEIGHT/2

    x_change = 0
    y_change = 0

    snake = []
    length = 1

    foodx = round(random.randrange(0, WIDTH - snake_block) / 10.0) * 10
    foody = round(random.randrange(0, HEIGHT - snake_block) / 10.0) * 10

    while not game_over:

        while game_close:
            screen.fill(black)
            message("Game Over! Press C to Play Again or Q to Quit", red)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        game()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x_change = -snake_block
                    y_change = 0
                elif event.key == pygame.K_RIGHT:
                    x_change = snake_block
                    y_change = 0
                elif event.key == pygame.K_UP:
                    y_change = -snake_block
                    x_change = 0
                elif event.key == pygame.K_DOWN:
                    y_change = snake_block
                    x_change = 0

        if x >= WIDTH or x < 0 or y >= HEIGHT or y < 0:
            game_close = True

        x += x_change
        y += y_change
        screen.fill(black)

        pygame.draw.rect(screen, red, [foodx, foody, snake_block, snake_block])

        snake_head = []
        snake_head.append(x)
        snake_head.append(y)
        snake.append(snake_head)

        if len(snake) > length:
            del snake[0]

        for block in snake[:-1]:
            if block == snake_head:
                game_close = True

        draw_snake(snake_block, snake)

        pygame.display.update()

        if x == foodx and y == foody:
            foodx = round(random.randrange(0, WIDTH - snake_block) / 10.0) * 10
            foody = round(random.randrange(0, HEIGHT - snake_block) / 10.0) * 10
            length += 1

        clock.tick(snake_speed)

    pygame.quit()
    quit()

game()