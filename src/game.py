from itertools import cycle
import random
import sys
import os
import argparse
import pickle
from IA import FbIa

import pygame
from pygame.locals import *

sys.path.append(os.getcwd())

flappyIA = FbIa(True)

SCREENWIDTH = 288
SCREENHEIGHT = 512
PIPEGAPSIZE = 100  # gap between upper and lower part of pipe
BASEY = SCREENHEIGHT * 0.79
# image, sound and hitmask  dicts
IMAGES, SOUNDS, HITMASKS = {}, {}, {}


def main():
    global SCREEN, FPSCLOCK, FPS, flappyIA

    parser = argparse.ArgumentParser("main.py")
    parser.add_argument("--fps", type=int, default=60, help="frames por segundo")
    parser.add_argument(
        "--dump_hitmasks", action="store_true", help="salvar as hitmasks em um arquivo"
    )
    args = parser.parse_args()

    FPS = args.fps

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
    pygame.display.set_caption('Bot Bird')

    # numbers sprites for score display
    IMAGES['numbers'] = (
        pygame.image.load('sprites/0.png').convert_alpha(),
        pygame.image.load('sprites/1.png').convert_alpha(),
        pygame.image.load('sprites/2.png').convert_alpha(),
        pygame.image.load('sprites/3.png').convert_alpha(),
        pygame.image.load('sprites/4.png').convert_alpha(),
        pygame.image.load('sprites/5.png').convert_alpha(),
        pygame.image.load('sprites/6.png').convert_alpha(),
        pygame.image.load('sprites/7.png').convert_alpha(),
        pygame.image.load('sprites/8.png').convert_alpha(),
        pygame.image.load('sprites/9.png').convert_alpha()
    )

    # game over sprite
    IMAGES['gameover'] = pygame.image.load('sprites/gameover.png').convert_alpha()
    # message sprite for welcome screen
    IMAGES['message'] = pygame.image.load('sprites/message.png').convert_alpha()
    # base (ground) sprite
    IMAGES['base'] = pygame.image.load('sprites/base.png').convert_alpha()

    while True:
        # load day background sprite
        IMAGES['background'] = pygame.image.load('sprites/background-day.png').convert()

        # load yellow bird sprite
        IMAGES['player'] = (
            pygame.image.load('sprites/yellowbird-upflap.png').convert_alpha(),
            pygame.image.load('sprites/yellowbird-midflap.png').convert_alpha(),
            pygame.image.load('sprites/yellowbird-downflap.png').convert_alpha(),
        )

        # load green pipe sprite
        IMAGES['pipe'] = (
            pygame.transform.flip(
                pygame.image.load('sprites/pipe-green.png').convert_alpha(), False, True),
            pygame.image.load('sprites/pipe-green.png').convert_alpha(),
        )

        # hitmask for pipes
        HITMASKS['pipe'] = (
            get_hitmask(IMAGES['pipe'][0]),
            get_hitmask(IMAGES['pipe'][1]),
        )

        # hitmask for player
        HITMASKS['player'] = (
            get_hitmask(IMAGES['player'][0]),
            get_hitmask(IMAGES['player'][1]),
            get_hitmask(IMAGES['player'][2]),
        )

        if args.dump_hitmasks:
            with open("data/hitmasks_data.pkl", "wb") as output:
                pickle.dump(HITMASKS, output, pickle.HIGHEST_PROTOCOL)
            sys.exit()

        movement_info = show_welcome_animation()
        crash_info = main_game(movement_info)
        showGameOverScreen(crash_info)


def show_welcome_animation():
    """Shows welcome screen animation of flappy bird"""
    # index of player to blit on screen
    player_index = 0
    player_index_gen = cycle([0, 1, 2, 1])
    # iterator used to change player_index after every 5th iteration
    loop_iter = 0

    player_x = int(SCREENWIDTH * 0.2)
    player_y = int((SCREENHEIGHT - IMAGES['player'][0].get_height()) / 2)

    message_x = int((SCREENWIDTH - IMAGES['message'].get_width()) / 2)
    message_y = int(SCREENHEIGHT * 0.12)

    basex = 0
    # amount by which base can maximum shift to left
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    # player shm for up-down motion on welcome screen
    playerShmVals = {'val': 0, 'dir': 1}

    while True:
        # desativando do jogo original, já que só iremos treinar um flappyIA
        """for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return {
                    'player_y': player_y + playerShmVals['val'],
                    'basex': basex,
                    'player_index_gen': player_index_gen,
                }"""
        return {
            "player_y": player_y + playerShmVals["val"],
            "basex": basex,
            "player_index_gen": player_index_gen,
        }

        # adjust player_y, player_index, basex
        if (loop_iter + 1) % 5 == 0:
            player_index = next(player_index_gen)
        loop_iter = (loop_iter + 1) % 30
        basex = -((-basex + 4) % baseShift)
        playerShm(playerShmVals)

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0, 0))
        SCREEN.blit(IMAGES['player'][player_index],
                    (player_x, player_y + playerShmVals['val']))
        SCREEN.blit(IMAGES['message'], (message_x, message_y))
        SCREEN.blit(IMAGES['base'], (basex, BASEY))

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def main_game(movement_info):
    score = player_index = loop_iter = 0
    player_index_gen = movement_info['player_index_gen']
    player_x, player_y = int(SCREENWIDTH * 0.2), movement_info['player_y']

    basex = movement_info['basex']
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    # get 2 new pipes to add to upper_pipes lower_pipes list
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # list of upper pipes
    upperPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[0]['y']},
    ]

    # list of lowerpipe
    lowerPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[1]['y']},
    ]

    pipeVelX = -4

    # player velocity, max velocity, downward accleration, accleration on flap
    playerVelY = -9  # player's velocity along Y, default same as playerFlapped
    playerMaxVelY = 10  # max vel along Y, max descend speed
    playerMinVelY = -8  # min vel along Y, max ascend speed
    playerAccY = 1  # players downward accleration
    playerFlapAcc = -9  # players speed on flapping
    playerFlapped = False  # True when player flaps

    while True:
        """ aqui, por meio de heuristicas, dizemos que o jogador não consegue ver uma pipe quando ele já estiver 
               mais de 30 pixels dentro """
        if -player_x + lowerPipes[0]["x"] > -30:
            my_pipe = lowerPipes[0]
        else:
            my_pipe = lowerPipes[1]

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

        if flappyIA.act(player_x, player_y , playerVelY, lowerPipes):
            if player_y > -2 * IMAGES['player'][0].get_height():
                playerVelY = playerFlapAcc
                playerFlapped = True

        # check for crash here
        crashTest = check_crash({'x': player_x, 'y': player_y, 'index': player_index},
                                upperPipes, lowerPipes)
        if crashTest[0]:
            # atualizamos os valores da q-table
            flappyIA.update_scores()

            return {
                'y': player_y,
                'groundCrash': crashTest[1],
                'basex': basex,
                'upper_pipes': upperPipes,
                'lower_pipes': lowerPipes,
                'score': score,
                'playerVelY': playerVelY,
            }

        # check for score
        playerMidPos = player_x + IMAGES['player'][0].get_width() / 2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + IMAGES['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1

        # player_index basex change
        if (loop_iter + 1) % 3 == 0:
            player_index = next(player_index_gen)
        loop_iter = (loop_iter + 1) % 30
        basex = -((-basex + 100) % baseShift)

        # player's movement
        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY
        if playerFlapped:
            playerFlapped = False

        playerHeight = IMAGES['player'][player_index].get_height()
        player_y += min(playerVelY, BASEY - player_y - playerHeight)

        # move pipes to left
        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            uPipe['x'] += pipeVelX
            lPipe['x'] += pipeVelX

        # add new pipe when first pipe is about to touch left of screen
        if len(upperPipes) > 0 and 0 < upperPipes[0]['x'] < 5:
            newPipe = getRandomPipe()
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1])

        # remove first pipe if its out of the screen
        if len(upperPipes) > 0 and upperPipes[0]['x'] < -IMAGES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0, 0))

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
            SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        SCREEN.blit(IMAGES['base'], (basex, BASEY))
        # print score so player overlaps the score
        show_score(score)
        SCREEN.blit(IMAGES["player"][player_index], (player_x, player_y))

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def showGameOverScreen(crashInfo):
    """crashes the player down ans shows gameover image"""
    score = crashInfo['score']
    playerx = SCREENWIDTH * 0.2
    playery = crashInfo['y']
    playerHeight = IMAGES['player'][0].get_height()
    playerVelY = crashInfo['playerVelY']
    playerAccY = 2

    basex = crashInfo['basex']

    upperPipes, lowerPipes = crashInfo['upper_pipes'], crashInfo['lower_pipes']

    while True:
        """for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery + playerHeight >= BASEY - 1:
                    return"""
        return
        # player y shift
        if playery + playerHeight < BASEY - 1:
            playery += min(playerVelY, BASEY - playery - playerHeight)

        # player velocity change
        if playerVelY < 15:
            playerVelY += playerAccY

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0, 0))

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
            SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        SCREEN.blit(IMAGES['base'], (basex, BASEY))
        show_score(score)
        SCREEN.blit(IMAGES["player"][1], (playerx, playery))

        FPSCLOCK.tick(FPS)
        pygame.display.update()


def playerShm(player_shm):
    """oscillates the value of player_shm['val'] between 8 and -8"""
    if abs(player_shm['val']) == 8:
        player_shm['dir'] *= -1

    if player_shm['dir'] == 1:
        player_shm['val'] += 1
    else:
        player_shm['val'] -= 1


def getRandomPipe():
    """returns a randomly generated pipe"""
    # y of gap between upper and lower pipe
    gap_y = random.randrange(0, int(BASEY * 0.6 - PIPEGAPSIZE))
    gap_y += int(BASEY * 0.2)
    pipe_height = IMAGES['pipe'][0].get_height()
    pipe_x = SCREENWIDTH + 10

    return [
        {'x': pipe_x, 'y': gap_y - pipe_height},  # upper pipe
        {'x': pipe_x, 'y': gap_y + PIPEGAPSIZE},  # lower pipe
    ]


def show_score(score):
    """displays score in center of screen"""
    score_digits = [int(x) for x in list(str(score))]
    total_width = 0  # total width of all numbers to be printed

    for digit in score_digits:
        total_width += IMAGES['numbers'][digit].get_width()

    xoffset = (SCREENWIDTH - total_width) / 2

    for digit in score_digits:
        SCREEN.blit(IMAGES['numbers'][digit], (xoffset, SCREENHEIGHT * 0.1))
        xoffset += IMAGES['numbers'][digit].get_width()


def check_crash(player, upper_pipes, lower_pipes):
    """returns True if player collders with base or pipes."""
    pi = player['index']
    player['w'] = IMAGES['player'][0].get_width()
    player['h'] = IMAGES['player'][0].get_height()

    # if player crashes into ground
    if player['y'] + player['h'] >= BASEY - 1:
        return [True, True]
    else:

        player_rect = pygame.Rect(player['x'], player['y'],
                                  player['w'], player['h'])
        pipe_w = IMAGES['pipe'][0].get_width()
        pipe_h = IMAGES['pipe'][0].get_height()

        for uPipe, lPipe in zip(upper_pipes, lower_pipes):
            # upper and lower pipe rects
            u_pipe_rect = pygame.Rect(uPipe['x'], uPipe['y'], pipe_w, pipe_h)
            l_pipe_rect = pygame.Rect(lPipe['x'], lPipe['y'], pipe_w, pipe_h)

            # player and upper/lower pipe hitmasks
            p_hitmask = HITMASKS['player'][pi]
            u_hitmask = HITMASKS['pipe'][0]
            l_hitmask = HITMASKS['pipe'][1]

            # if bird collided with upipe or lpipe
            u_collide = pixel_collision(player_rect, u_pipe_rect, p_hitmask, u_hitmask)
            l_collide = pixel_collision(player_rect, l_pipe_rect, p_hitmask, l_hitmask)

            if u_collide or l_collide:
                return [True, False]

    return [False, False]


def pixel_collision(rect1, rect2, hitmask1, hitmask2):
    """Checks if two objects collide and not just their rects"""
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - rect1.x, rect.y - rect1.y
    x2, y2 = rect.x - rect2.x, rect.y - rect2.y

    for x in range(rect.width):
        for y in range(rect.height):
            if hitmask1[x1 + x][y1 + y] and hitmask2[x2 + x][y2 + y]:
                return True
    return False


def get_hitmask(image):
    """returns a hitmask using an image's alpha."""
    mask = []
    for x in range(image.get_width()):
        mask.append([])
        for y in range(image.get_height()):
            mask[x].append(bool(image.get_at((x, y))[3]))
    return mask


if __name__ == '__main__':
    main()
