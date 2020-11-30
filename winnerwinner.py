from pygame.locals import *

import pygame
import sys
import random
import math
import time


pygame.init()

surf = pygame.display.set_mode((800, 600), 0, 32)
pygame.display.set_caption('Winner! Winner!')

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

ammo_speed = 6
charger = 7
reloading_time = 150
crited = 3.0
full_blood = 60
movement = 5
around = 60
border = 15

def init_models():
    return {'red': {'dir': {'up': 0, 'right': 0},
                    'point': (250, 150), 'radius': 40,
                    'color': RED, 'blood': full_blood,
                    'reloading': 0, 'need_reload': False,
                    'charger': charger, 'ammo_color': YELLOW},
            'blue': {'dir': {'up': 0, 'right': 0},
                     'point': (550, 150), 'radius': 40,
                     'color': BLUE, 'blood': full_blood,
                     'reloading': 0, 'need_reload': False,
                     'charger': charger, 'ammo_color': WHITE}}

def init_ammos():
    return {'red': [], 'blue': []}

def init_msg():
    return {'red': [], 'blue': []}               

def roll():
    return random.randint(1, 20)

def move():
    while True:
        up = random.sample([-1, 1], 1)[0]
        right = random.sample([-1, 1], 1)[0]
        if roll() == 1 and roll() > 10:
            up = 0
        if roll() == 20 and roll() <= 10:
            right = 0
        if up == 0 and right == 0:
            continue
        elif up == 0:
            right = right * movement
        elif right == 0:
            up = up * movement
        else:
            degree = random.randint(1, 89)
            radian = math.pi * degree * 2 / 360
            up = math.sin(radian) * movement * up
            right = math.cos(radian) * movement * right
            return up, right

def shoot(c):
    x, y = models[c]['point']
    other = 'blue' if c == 'red' else 'red'
    ox, oy = models[other]['point']
    scale = math.sqrt(abs(ox - x) ** 2 + abs(oy - y) ** 2) / models[c]['radius']
    point = (x + (ox - x) / scale, y + (oy - y) / scale)
    if abs(ox - x) != 0 and abs(oy - y) != 0:
        if abs(ox -x) >= abs(oy - y):
            ratio = abs(ox - x) / abs(oy - y)
            shorter = 'y'
        else:
            ratio = abs(oy - y) / abs(ox - x)
            shorter = 'x'
        short = math.sqrt(ammo_speed * math.sqrt(2) ** 2 / (1 + ratio ** 2))
        if shorter == 'y':
            up = -short if oy -y > 0 else short
            right = -short * ratio if ox - x < 0 else short * ratio
        else:
            right = -short if ox -x < 0 else short
            up = -short * ratio if oy - y > 0 else short * ratio
    elif abs(ox - x) == 0:
        up = (y - oy) * ammo_speed
        right = 0
    elif abs(oy - y) == 0:
        up = 0
        right = (ox - x) * ammo_speed

    ammo = {'dir': {'up': up, 'right': right}, 'point': point, 'radius': 3, 'color': models[c]['ammo_color']}
    ammos[c].append(ammo)


def game_init():
    global ammos
    global models
    global msg_queue
    global loop
    global winner
    ammos = init_ammos()
    models = init_models()
    msg_queue = init_msg()
    loop = max_loop
    winner = None
    

def printxt(size, text, clr, x, y):
    basic_font = pygame.font.SysFont(None, size)
    t = basic_font.render(text, True, clr)
    r = t.get_rect()
    r.centerx = x
    r.centery = y
    surf.blit(t, r)

models = init_models()
fly_warning = False
max_loop = 30
started = False

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN and event.key == ord('a'):
            game_init()
            started = True

    if not started:
        surf.fill(BLACK)
        for m in models.values():
            pygame.draw.circle(surf, m['color'], m['point'], m['radius'])
        printxt(48, 'WHO CAN WIN?', WHITE, *(surf.get_rect().centerx, surf.get_rect().centery + 50))
        printxt(40, 'PRESS [A] START', WHITE, *(surf.get_rect().centerx, surf.get_rect().centery + 270))
        pygame.display.update()
        continue

    if 'winner' in dir() and winner:
        surf.fill(BLACK)
        for m in models.values():
            pygame.draw.circle(surf, m['color'], m['point'], m['radius'])
            printxt(35, str(m['blood']), WHITE, *m['point'])
        printxt(45, winner.upper() + ' WIN', models[winner]['color'],
                *(surf.get_rect().centerx, 30))
        printxt(45, 'CELEBRATE!', models[winner]['color'],
                *(surf.get_rect().centerx, 60))
        printxt(40, 'PRESS [A] RESTART', WHITE, *(surf.get_rect().centerx, surf.get_rect().centery + 270))
        pygame.display.update()
        continue

    if started:
        surf.fill(BLACK)
        # change directions
        loop += 1
        if not fly_warning and loop >= max_loop and roll() > 2:
            for k, m in models.items():
                up, right = move()
                m['dir']['up'] = up
                m['dir']['right'] = right
            loop = 0
        # keep away from borders and each other
        for m in models.values():
            x, y = m['point']
            surf_width, surf_height = pygame.display.get_window_size()
            if x <= m['radius'] + border:
                m['dir']['right'] = movement
                m['dir']['up'] = 0
            elif x >= surf_width - m['radius'] - border:
                m['dir']['right'] = -movement
                m['dir']['up'] = 0
            if y <= m['radius'] + border:
                m['dir']['up'] = -movement
                m['dir']['right'] = 0
            elif y >= surf_height - m['radius'] - border:
                m['dir']['up'] = movement
                m['dir']['right'] = 0
        redx, redy = models['red']['point']
        bluex, bluey = models['blue']['point']
        if not fly_warning and math.sqrt(abs(redx - bluex) ** 2 + abs(redy - bluey) ** 2) <= (models['red']['radius'] + around) * 2:
            fly_warning = True
            for k, m in models.items():
                m['dir']['up'] = -m['dir']['up']
                m['dir']['right'] = -m['dir']['right']
        else:
            fly_warning = False
        # all flying to new points
        for c, m in models.items():
            x, y = m['point']
            m['point'] = (x + m['dir']['right'], y - m['dir']['up'])
            pygame.draw.circle(surf, m['color'], m['point'], m['radius'])
            models[c]['point'] = m['point']
            locx, locy = m['point']
            printxt(35, str(m['blood']), WHITE, *(locx, locy - 10))
        # shoot and reload
        for c, m in models.items():
            if models[c]['need_reload']:
                if models[c]['reloading'] == 0:
                    msg_queue[c].append('reload')
                models[c]['reloading'] += 1
            if models[c]['reloading'] >= reloading_time:
                models[c]['charger'] = charger
                models[c]['reloading'] = 0
                models[c]['need_reload'] = False
                msg_queue[c].append('loaded')
            if models[c]['charger'] > 0:
                if roll() > 5:
                    if roll() == 20:
                        shoot(c)
                        models[c]['charger'] -= 1
                if models[c]['charger'] == 0:
                    models[c]['need_reload'] = True
        # ammos flying and make damage if hit
        for c, v in ammos.items():
            for i, a in enumerate(v):
                pygame.draw.circle(surf, a['color'], a['point'], a['radius'])
                other = 'blue' if c == 'red' else 'red'
                x, y = a['point']
                tx, ty = models[other]['point']
                if math.sqrt(abs(tx - x) ** 2 + abs(ty - y) ** 2) <= models[other]['radius']:
                    mode = 'grazed' if roll() < 13 else 'hitted'
                    if mode == 'grazed':
                        damage = random.sample([1, 2, 3], 1)[0]
                    elif mode == 'hitted':
                        damage = 5
                    if mode == 'hitted' and roll() > 15:
                        mode = 'critted'
                        damage *= crited
                        damage = int(damage)
                    models[other]['blood'] -= damage
                    ammos[c].pop(i)
                    prompt = '-' + str(damage)
                    if mode == 'grazed':
                        prompt = 'grazed'
                    elif mode == 'critted':
                        prompt = 'critted'
                    msg_queue[other].append(prompt)
                    if models[other]['blood'] <= 0:
                        winner = c
                else:
                    x, y = a['point']
                    x += ammo_speed * a['dir']['right']
                    y -= ammo_speed * a['dir']['up']
                    ammos[c][i]['point'] = (x, y)
        # print each last msg
        for c, m in models.items():
            if msg_queue[c]:
                x, y = m['point']
                printxt(25, msg_queue[c][-1], WHITE, *(x, y + 15))

        pygame.display.update()

    time.sleep(0.02)
