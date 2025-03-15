from collections import defaultdict
import numpy as np
import pygame as pg
import random

width, height = 700, 450
FPS = 60

BLACK = (0, 0, 0)

x_direction = 0
y_direction = 0
player_speed = 2
images_dict = {
    'bg': pg.image.load('img/Background.png'),
    'player': {
        'rear': pg.image.load('img/cab_rear.png'),
        'left': pg.image.load('img/cab_left.png'),
        'front': pg.image.load('img/cab_front.png'),
        'right': pg.image.load('img/cab_right.png'),
    },
    'assets':{
        'hole': pg.image.load('img/hole.png'),
        'hotel': pg.transform.scale(pg.image.load('img/hotel.png'), (80,80)),
        'passenger': pg.image.load('img/passenger.png'),
        'taxi_background':  pg.transform.scale(pg.image.load('img/taxi_background.png'), (80, 45)),
    },
}

# Таксі
player_view = 'rear'
player_rect = images_dict['player'][player_view].get_rect()
player_rect.x = 300
player_rect.y = 300

# Готель
hotel_img = images_dict['assets']['hotel']
hotel_rect = hotel_img.get_rect()
hotel_positions = [
    (60, 30),
    (555, 30),
    (60, 250),
    (555, 250)
]
hotel_rect.x, hotel_rect.y = random.choice(hotel_positions)



# Парковочне місце
parking_img = images_dict['assets']['taxi_background']
parking_rect = parking_img.get_rect()
parking_rect.x, parking_rect.y = hotel_rect.x, hotel_rect.y + hotel_rect.height

# Пасажир
passenger_img = images_dict['assets']['passenger']
passenger_rect = passenger_img.get_rect()
# passenger_rect.x, passenger_rect.y = hotel_rect.x, hotel_rect.y + hotel_rect.height
passenger_rect.x, passenger_rect.y = random.choice(hotel_positions)
passenger_rect.y += hotel_rect.height

def apply_action(action):
    if action is None:
        return
    global player_view
    x_direction = 0
    y_direction = 0
    if action == 0:
        #and player_rect.x < width - player_rect.width
        x_direction = 1
        player_view = 'right'
    elif action == 1:
        # and player_rect.x > 0
        x_direction = -1
        player_view = 'left'
    elif action == 2:
        # and player_rect.y > 0
        y_direction = -1
        player_view = 'rear'
    elif action == 3:
        # and player_rect.y <= height - player_rect.height
        y_direction = 1
        player_view = 'front'

    new_x = player_rect.x + player_rect.width * x_direction
    new_y = player_rect.y + player_rect.height * y_direction

    player_rect.x, player_rect.y = new_x, new_y

def is_crash():
    for x in range(player_rect.x, player_rect.topright[0], 1):
        for y in range(player_rect.y, player_rect.bottomleft[1], 1):
            try:
                if screen.get_at((x,y)) == (220, 215, 177):
                    return True
            except IndexError:
                print("назад в діапазон")
    if hotel_rect.colliderect(player_rect):
        return True
    return False

def draw_message(text, color):
    font = pg.font.SysFont(None, 36)
    message = font.render(text, True, color)
    screen.blit(message, (350, 150))
    pg.display.flip()
    pg.time.delay(4000)

########################################################################
# Q_learning

actions = [0, 1, 2, 3]  # 0 - right, 1 - left, 2 - up, 3 - down

# (300, 300): [1, 3, 2, -3]
Q_tabel = defaultdict(lambda: [0, 0, 0, 0])

learning_rate = 0.9
discount_factor = 0.9
epsilon = 0.1

def draw():
    # Візуалізація
    screen.fill(BLACK)
    screen.blit(images_dict['bg'], (0, 0))
    # Промальовка
    screen.blit(images_dict['assets']['hotel'], hotel_rect)
    screen.blit(images_dict['assets']['taxi_background'], parking_rect)
    screen.blit(images_dict['assets']['passenger'], passenger_rect)
    screen.blit(images_dict['player'][player_view], player_rect)

    pg.display.flip()

def choose_action(state):
    if random.random() < epsilon:
        return random.choice(actions)
    else:
        return np.argmax(Q_tabel[state])


def update_q(state, action, reward, next_state):
    best_next = max(Q_tabel[next_state])
    Q_tabel[state][action] += learning_rate * (reward + discount_factor * best_next - Q_tabel[state][action])


def make_step():
    current_state = (player_rect.x, player_rect.y)
    action = choose_action(current_state)
    apply_action(action)
    # draw
    draw()
    reward = -1
    episode_end = False
    success = False

    if is_crash():
        reward = -100
        episode_end = True

    if parking_rect.contains(player_rect):
        reward = 100
        episode_end = True
        success = True

    next_state = (player_rect.x, player_rect.y)
    update_q(current_state, action, reward, next_state)
    return (episode_end, success)

pg.init()

screen = pg.display.set_mode([width, height])

# Основний цикл навчання
num_episodes = 300
max_steps = 50

for episode in range(num_episodes):
    player_rect.x = 300
    player_rect.y = 300
    for step in range(max_steps):
        (episode_end, success) = make_step()
        if episode_end:
            print("Win? -", success)
            break
print(Q_tabel)

draw_message("Таксі навчилося!", pg.Color("blue"))
########################################################################





timer = pg.time.Clock()

run = True
while run:
    timer.tick(FPS)

    current_state = (player_rect.x, player_rect.y)
    action = choose_action(current_state)
    apply_action(action)

    # Події
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
    # keys_klava = pg.key.get_pressed()
    #
    # if keys_klava[pg.K_RIGHT]:
    #     #and player_rect.x < width - player_rect.width
    #     x_direction = 1
    #     player_view = 'right'
    # elif keys_klava[pg.K_LEFT]:
    #     # and player_rect.x > 0
    #     x_direction = -1
    #     player_view = 'left'
    # elif keys_klava[pg.K_UP]:
    #     # and player_rect.y > 0
    #     y_direction = -1
    #     player_view = 'rear'
    # elif keys_klava[pg.K_DOWN]:
    #     # and player_rect.y <= height - player_rect.height
    #     y_direction = 1
    #     player_view = 'front'
    #
    # if player_rect.x <= 0:
    #     player_rect.x = width - player_rect.width
    # elif player_rect.x >= width - player_rect.width:
    #     player_rect.x = 0
    # elif player_rect.y >= height - player_rect.height:
    #     player_rect.y = 0
    # elif player_rect.y <= 0:
    #     player_rect.y = height - player_rect.height

    # Поновлення
    player_rect.x += player_speed * x_direction
    player_rect.y += player_speed * y_direction
    x_direction = 0
    y_direction = 0

    if is_crash():
        print("IS CRASH")
        # run = False
        player_view = 'rear'
        player_rect.x = 300
        player_rect.y = 300
        passenger_rect.x, passenger_rect.y = random.choice(hotel_positions)
        passenger_rect.y += hotel_rect.height
        reward = -100
        episode_end = False
        continue

    if parking_rect.contains(player_rect):
        # passenger_rect.x, passenger_rect.y = player_rect.x, player_rect.y + player_rect.height
        draw_message("Перермога!!!", pg.Color('green'))
        player_view = 'rear'
        player_rect.x = 300
        player_rect.y = 300

        hotel_rect.x, hotel_rect.y = random.choice(hotel_positions)
        parking_rect.x, parking_rect.y = hotel_rect.x, hotel_rect.y + hotel_rect.height
        passenger_rect.x, passenger_rect.y = random.choice(hotel_positions)
        passenger_rect.y += hotel_rect.height
        reward = 100
        episode_end = True
        success = True
        continue

    if player_rect.colliderect(passenger_rect):
        passenger_rect.x, passenger_rect.y = player_rect.x, player_rect.y


    # Візуалізація
    # screen.fill(BLACK)
    # screen.blit(images_dict['bg'], (0, 0))

    # Промальовка
    # screen.blit(images_dict['assets']['hotel'], hotel_rect)
    # screen.blit(images_dict['assets']['taxi_background'], parking_rect)
    # screen.blit(images_dict['assets']['passenger'], passenger_rect)
    # screen.blit(images_dict['player'][player_view], player_rect)
    #
    # pg.display.flip()

    draw()

pg.quit()