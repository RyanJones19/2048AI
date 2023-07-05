import pygame
import neat
import time
import random
import os
import math
import copy
pygame.font.init()


WIN_WIDTH = 1000
WIN_HEIGHT = 1000
TILE_WIDTH = 28
TILE_HEIGHT = 32

BOARD_IMAGE = pygame.image.load(os.path.join("imgs", "BaseBoard.png"))
TILE_0 = pygame.image.load(os.path.join("imgs", "0.png"))
TILE_2 = pygame.image.load(os.path.join("imgs", "2.png"))
TILE_4 = pygame.image.load(os.path.join("imgs", "4.png"))
TILE_8 = pygame.image.load(os.path.join("imgs", "8.png"))
TILE_16 = pygame.image.load(os.path.join("imgs", "16.png"))
TILE_32 = pygame.image.load(os.path.join("imgs", "32.png"))
TILE_64 = pygame.image.load(os.path.join("imgs", "64.png"))
TILE_128 = pygame.image.load(os.path.join("imgs", "128.png"))
TILE_256 = pygame.image.load(os.path.join("imgs", "256.png"))
TILE_512 = pygame.image.load(os.path.join("imgs", "512.png"))
TILE_1024 = pygame.image.load(os.path.join("imgs", "1024.png"))
TILE_2048 = pygame.image.load(os.path.join("imgs", "2048.png"))

STAT_FONT = pygame.font.SysFont("comicsans", 50)

position_map = {}

for i in range(16):
    row = i // 4
    col = i % 4
    x = 28 + col * 242
    y = 32 + row * 242
    position_map[str(i+1)] = {"row": row, "col": col, "x": x, "y": y}

integer_to_image_map = {
    0: TILE_0,
    2: TILE_2,
    4: TILE_4,
    8: TILE_8,
    16: TILE_16,
    32: TILE_32,
    64: TILE_64,
    128: TILE_128,
    256: TILE_256,
    512: TILE_512,
    1024: TILE_1024,
    2048: TILE_2048
}

class Game:
    def __init__(self):
        self.score = 0
        self.run = True
        self.win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        self.board = Board(self.win)

    def draw_window(self):
        pygame.display.update()
        

class Board:
    def __init__(self, win):
        self.win = win
        self.draw()
        self.board = [[Tile(0, position_map[str(i*4+j+1)]["x"], position_map[str(i*4+j+1)]["y"]) for j in range(4)] for i in range(4)]
        for row in self.board:
            for tile in row:
                tile.draw(self.win)
        random_starting_tiles = random.sample(range(1, 17), 2)
        self.add_tile(self.select_two_or_four(), random_starting_tiles[0])
        self.add_tile(self.select_two_or_four(), random_starting_tiles[1])

    def select_two_or_four(self):
        return random.choice([2, 4])


    def add_tile(self, value, position):
        tile = Tile(value, position_map[str(position)]["x"], position_map[str(position)]["y"])
        self.board[position_map[str(position)]["row"]][position_map[str(position)]["col"]] = tile
        tile.draw(self.win)
        return tile

    def select_random_empty_tile(self):
        empty_tiles = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                if self.board[row][col].value == 0:
                    for key, value in position_map.items():
                        if value["row"] == row and value["col"] == col:
                            empty_tiles.append(int(key))
        return random.choice(empty_tiles)

    def update_board(self):
        for i in range(4):
            for j in range(4):
                for key, value in position_map.items():
                    if value["row"] == i and value["col"] == j:
                        self.board[i][j].row = value["x"]
                        self.board[i][j].col = value["y"]
        for row in self.board:
            for tile in row:
                tile.draw(self.win)
            
    def draw(self):
        self.win.blit(BOARD_IMAGE, (0, 0))

    def move_left(self, board):
        changed = False

        for row in board:
            old_row = row[:]
            zeros = [tile for tile in row if tile.value == 0]
            row[:] = [tile for tile in row if tile.value != 0] + zeros
            if row != old_row:
                changed = True
            for tile in range(len(row) - 1):
                if row[tile].value == row[tile + 1].value and row[tile].value != 0:
                    row[tile].value *= 2
                    row[tile + 1].value = 0
                    changed = True
            zeros = [tile for tile in row if tile.value == 0]
            row[:] = [tile for tile in row if tile.value != 0] + zeros

        return changed

    def move_right(self, board):
        reversed_board = [row[::-1] for row in board]
        changed = self.move_left(reversed_board)
        self.board = [row[::-1] for row in reversed_board]
        return changed

    def move_up(self, board):
        transposed_board = list(map(list, zip(*board)))
        changed = self.move_left(transposed_board)
        self.board = list(map(list, zip(*transposed_board)))
        return changed

    def move_down(self, board):
        reversed_transposed_board = list(map(list, zip(*board[::-1])))
        changed = self.move_left(reversed_transposed_board)
        self.board = list(map(list, zip(*reversed_transposed_board)))[::-1]
        return changed

    def try_all_moves(self, board):
        if self.move_left(board) or self.move_right(board) or self.move_up(board) or self.move_down(board):
            self.update_board()
            self.add_tile(self.select_two_or_four(), self.select_random_empty_tile())
            pygame.display.update()
            return True
        else:
            return False

    def try_next_move(self, board, suggested_order):
        for move in suggested_order:
            if move == 0:
                if self.move_left(board):
                    return True
            elif move == 1:
                if self.move_right(board):
                    return True
            elif move == 2:
                if self.move_up(board):
                    return True
            elif move == 3:
                if self.move_down(board):
                    return True
        return False


    def calculate_max_tile(self, board):
        max_tile = 0
        for row in board:
            for tile in row:
                if tile.value > max_tile:
                    max_tile = tile.value
        return max_tile

    def count_zeros(self,board):
        zeros = 0
        for row in board:
            for tile in row:
                if tile.value == 0:
                    zeros += 1
        return zeros

    # In rows 0 and 2 if the tile to the right is the same value or half the value, add to fitness
    # In rows 1 and 3 if the tile to the right is the same value of double the value, add to fitness
    def calculate_board_smoothness(self,board):
        smoothness = 0
        for row in range(4):
            for tile in range(3):
                if row == 0 or row == 2:
                    if board[row][tile].value == board[row][tile+1].value or board[row][tile].value == board[row][tile+1].value/2:
                        smoothness += 1
                else:
                    if board[row][tile].value == board[row][tile+1].value or board[row][tile].value == board[row][tile+1].value*2:
                        smoothness += 1
        print("Smoothness was ", smoothness)
        return smoothness

    def calculate_board_state_fitness(self, board):
        fitness = 0
        positional_weights = [[16,15,14,13],[9,10,11,12],[8,7,6,5],[4,3,2,1]]
        for row_position, row in enumerate(board):
            for tile_position, tile in enumerate(row):
                fitness += tile.value * positional_weights[row_position][tile_position]
        print("Fitness was ", fitness)
        return fitness * self.count_zeros(board) * self.calculate_board_smoothness(board)



class Tile:
    def __init__(self, value, x, y):
        self.value = value
        self.row = x
        self.col = y

    def draw(self, win):
        tile_img = integer_to_image_map[self.value]
        win.blit(tile_img, (self.row, self.col))
        

def game_loop(genomes, config):
    game = Game()
    could_move_left = True
    could_move_right = True
    could_move_up = True
    could_move_down = True
    max_tile = 0

    nets = []
    ge = []
    games = []
    #scores = []
    #time.sleep(10)

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        game = Game()
        games.append(game)
        #scores.append(0)
        g.fitness = 0
        ge.append(g)

    #while game.run:
    run = True
    while run:
        #print("Finished trying to move in all 50 Games")
        #time.sleep(3)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        print("Number of remaining games in species: ", len(games))
        #print(could_move_left, could_move_right, could_move_up, could_move_down)
        if len(games) == 0:
            run = False
            print("MAX TILE THIS GAME:", max_tile)
            time.sleep(5)
            break
        for x, game in enumerate(games):
            #time.sleep(1)
            print(x)
            print(len(ge))
            print(len(games))
            game.draw_window()
            ge[x].fitness += 1
            output = nets[x].activate((game.board.board[0][0].value, 
                                       game.board.board[0][1].value, 
                                       game.board.board[0][2].value, 
                                       game.board.board[0][3].value, 
                                       game.board.board[1][0].value, 
                                       game.board.board[1][1].value, 
                                       game.board.board[1][2].value, 
                                       game.board.board[1][3].value, 
                                       game.board.board[2][0].value, 
                                       game.board.board[2][1].value, 
                                       game.board.board[2][2].value, 
                                       game.board.board[2][3].value, 
                                       game.board.board[3][0].value, 
                                       game.board.board[3][1].value, 
                                       game.board.board[3][2].value, 
                                       game.board.board[3][3].value))
            print(output)
            board_max_tile = game.board.calculate_max_tile(game.board.board)
            if board_max_tile > max_tile:
                max_tile = board_max_tile
                
            # get the index of the max value in the output list if there are equal values in the list, the first one is returned
            max_index = output.index(max(output))
            # create a new list containing the values 0 through 3 ordered based on the output index list
            # for example if index 2 is largest and index 1 is second largest the list would be [2,1,0,3]
            suggested_moves = sorted(range(len(output)), key=lambda k: output[k], reverse=True)
            print(suggested_moves)
            #if output[0] > 0.5:
            if max_index == 0:
                print("Trying to move left")
                # Create a copy of the game board that can be compared to the board after the move
                boardBeforeMove = copy.deepcopy(game.board.board)

                # print the game board before the move in 4x4 as text
                #for row in boardBeforeMove:
                #    for tile in row:
                #        print(tile.value, end=" ")
                #    print()

                #numMerges = 0
                # Starting in the upper left corner, compare each tile to the tile to its right if their values match add one to numMerges
                #for row in range(4):
                #    for col in range(3):
                #        if game.board.board[row][col].value == game.board.board[row][col+1].value:
                #            numMerges += 1

                #print("=====================================")
                could_move_left = game.board.move_left(game.board.board)
                print("Could move left: ", could_move_left)
                # print the game board after the move
                #for row in game.board.board:
                #    for tile in row:
                #        print(tile.value, end=" ")
                #    print()
                # if the tile in the upper left corner after the move is the same or larger add 5 to the fitness
                #if game.board.board[0][0].value >= boardBeforeMove[0][0].value:
                #    try:
                #        ge[x].fitness += 3
                #    except:
                #        continue

                # if the tile in the upper left is the largest tile on the board add 10 to the fitness
                #largest_tile = True
                #for row in game.board.board:
                #    for tile in row:
                #        if tile.value > game.board.board[0][0].value:
                #            largest_tile = False
                #            break
                #if largest_tile:
                #    ge[x].fitness += 5

                if could_move_left:
                    #scores[x] += 1
                    try:
                        #ge[x].fitness += numMerges
                        ge[x].fitness += game.board.calculate_board_state_fitness(game.board.board) + 50
                    except:
                        continue
                    #print("UPDATING BOARD")
                    #time.sleep(2)
                    game.board.update_board()
                    game.board.add_tile(game.board.select_two_or_four(), game.board.select_random_empty_tile())
                    pygame.display.update()
                    could_move_left, could_move_right, could_move_up, could_move_down = True, True, True, True
                else:
                    #could_move_left = False
                    print("LEFT: INCORRECT")
                    #try:
                    #    ge[x].fitness -= 1
                    #except:
                    #    continue
                    #if not game.board.try_all_moves(game.board.board):
                    if game.board.try_next_move(game.board.board, suggested_moves):
                        game.board.update_board()
                        game.board.add_tile(game.board.select_two_or_four(), game.board.select_random_empty_tile())
                        pygame.display.update()
                    else:
                        ge[x].fitness -= 500
                        nets.pop(x)
                        ge.pop(x)
                        games.pop(x)
                        print("GAME OVER, REMOVED GAME")
                        #time.sleep(5)
                    #nets.pop(x)
                    #ge.pop(x)
                    #games.pop(x)
                    #print("Game completed with score: ", scores[x])
                    #scores.pop(x)
            #elif output[1] > 0.5:
            elif max_index == 1:
                print("Trying to move right")
                #numMerges = 0
                # Starting in the upper left corner, compare each tile to the tile to its right if their values match add one to numMerges
                #for row in range(4):
                #    for col in range(3):
                #        if game.board.board[row][col].value == game.board.board[row][col+1].value and game.board.board[row][col].value != 0:
                #            numMerges += 1
                could_move_right = game.board.move_right(game.board.board)

                if(game.board.board[0][0].value == 0):
                    ge[x].fitness -= 5
                elif(game.board.board[0][0].value == 2 or game.board.board[0][0] == 4):
                    ge[x].fitness -= 100
                print("Could move right? ", could_move_right)

                #if game.board.board[0][0].value != 0:
                #    ge[x].fitness += 3

                if could_move_right:
                    #scores[x] += 1
                    try:
                        #ge[x].fitness += 0.5*numMerges
                        ge[x].fitness += game.board.calculate_board_state_fitness(game.board.board)
                    except:
                        continue
                    game.board.update_board()
                    game.board.add_tile(game.board.select_two_or_four(), game.board.select_random_empty_tile())
                    pygame.display.update()
                    could_move_left, could_move_right, could_move_up, could_move_down = True, True, True, True
                else:
                    #could_move_right = False
                    print("RIGHT: INCORRECT")
                    #try:
                        #ge[x].fitness -= 1
                    #except:
                    #    continue
                    #if not game.board.try_all_moves(game.board.board):
                    if game.board.try_next_move(game.board.board, suggested_moves):
                        game.board.update_board()
                        game.board.add_tile(game.board.select_two_or_four(), game.board.select_random_empty_tile())
                        pygame.display.update()
                    else:
                        ge[x].fitness -= 500
                        nets.pop(x)
                        ge.pop(x)
                        games.pop(x)
                        print("GAME OVER, REMOVED GAME")
                        #time.sleep(5)
                    #nets.pop(x)
                    #ge.pop(x)
                    #games.pop(x)
                    #print("Game completed with score: ", scores[x])
                    #scores.pop(x)
            #elif output[2] > 0.5:
            elif max_index == 2:
                print("Trying to move up")
                #numMerges = 0
                # Starting in the upper left corner, compare each tile to the tile directly below it if their values match add one to numMerges
                #for row in range(3):
                #    for col in range(4):
                #        if game.board.board[row][col].value == game.board.board[row+1][col].value:
                #            numMerges += 1
                could_move_up = game.board.move_up(game.board.board)
                print("Could move up? ", could_move_up)
                if could_move_up:
                    #scores[x] += 1
                    try:
                        #ge[x].fitness += numMerges
                        ge[x].fitness += game.board.calculate_board_state_fitness(game.board.board) + 50
                    except:
                        continue
                    game.board.update_board()
                    game.board.add_tile(game.board.select_two_or_four(), game.board.select_random_empty_tile())
                    pygame.display.update()
                    could_move_left, could_move_right, could_move_up, could_move_down = True, True, True, True
                else:
                    #could_move_up = False
                    print("UP: INCORRECT")
                    #try:
                        #ge[x].fitness -= 1
                    #except:
                    #    continue
                    #if not game.board.try_all_moves(game.board.board):
                    if game.board.try_next_move(game.board.board, suggested_moves):
                        game.board.update_board()
                        game.board.add_tile(game.board.select_two_or_four(), game.board.select_random_empty_tile())
                        pygame.display.update()
                    else:
                        ge[x].fitness -= 500
                        nets.pop(x)
                        ge.pop(x)
                        games.pop(x)
                        print("GAME OVER, REMOVED GAME")
                        #time.sleep(5)

                    #nets.pop(x)
                    #ge.pop(x)
                    #games.pop(x)
                    #print("Game completed with score: ", scores[x])
                    #scores.pop(x)
            #elif output[3] > 0.5:
            elif max_index == 3:
                print("Trying to move down")
                #numMerges = 0
                # Starting in the upper left corner, compare each tile to the tile directly below it if their values match add one to numMerges
                #for row in range(3):
                #    for col in range(4):
                #        if game.board.board[row][col].value == game.board.board[row+1][col].value and game.board.board[row][col].value != 0:
                #            numMerges += 1
                could_move_down = game.board.move_down(game.board.board)

                if(game.board.board[0][0].value == 0):
                    ge[x].fitness -= 1000
                elif(game.board.board[0][0].value == 2 or game.board.board[0][0] == 4):
                    ge[x].fitness -= 5000
                print("Could move down? ", could_move_down)
                # after moving down if the tile in the upper left corner did not move then add 3 to the fitness
                #if game.board.board[0][0].value != 0:
                #    ge[x].fitness += 3
                if could_move_down:
                    #scores[x] += 1
                    try:
                        #ge[x].fitness -= 0.25*numMerges
                        ge[x].fitness += game.board.calculate_board_state_fitness(game.board.board)
                    except:
                        continue
                    game.board.update_board()
                    game.board.add_tile(game.board.select_two_or_four(), game.board.select_random_empty_tile())
                    pygame.display.update()
                    could_move_left, could_move_right, could_move_up, could_move_down = True, True, True, True
                else:
                    #could_move_down = False
                    print("DOWN: INCORRECT")
                    #try:
                        #ge[x].fitness -= 3
                    #except:
                    #    continue
                    #if not game.board.try_all_moves(game.board.board):
                    if game.board.try_next_move(game.board.board, suggested_moves):
                        game.board.update_board()
                        game.board.add_tile(game.board.select_two_or_four(), game.board.select_random_empty_tile())
                        pygame.display.update()
                    else:
                        nets.pop(x)
                        ge.pop(x)
                        games.pop(x)
                        print("GAME OVER, REMOVED GAME")
                        #time.sleep(5)

                    #nets.pop(x)
                    #ge.pop(x)
                    #games.pop(x)
                    #print("Game completed with score: ", scores[x])
                    #scores.pop(x)
            elif not could_move_left and not could_move_right and not could_move_up and not could_move_down:
                #print("Coult not move any direction")
                #print("Game over")
                #try:
                #    ge[x].fitness -= 10
                #except:
                #    continue
                ge[x].fitness -= 500
                nets.pop(x)
                ge.pop(x)
                games.pop(x)
                print("GAME OVER, REMOVED GAME")
                time.sleep(5)

                #print("Game completed with score: ", scores[x])
                #scores.pop(x)
            else:
                print("AI found no preferred direction to move, will try left, up, right, down")
                if(game.board.move_left(game.board.board)):
                    game.board.update_board()
                    game.board.add_tile(game.board.select_two_or_four(), game.board.select_random_empty_tile())
                    pygame.display.update()
                    #could_move_left, could_move_right, could_move_up, could_move_down = True, True, True, True
                    could_move_left = True
                elif(game.board.move_up(game.board.board)):
                    game.board.update_board()
                    game.board.add_tile(game.board.select_two_or_four(), game.board.select_random_empty_tile())
                    pygame.display.update()
                    #could_move_left, could_move_right, could_move_up, could_move_down = True, True, True, True
                    could_move_up = True
                elif(game.board.move_right(game.board.board)):
                    game.board.update_board()
                    game.board.add_tile(game.board.select_two_or_four(), game.board.select_random_empty_tile())
                    pygame.display.update()
                    #could_move_left, could_move_right, could_move_up, could_move_down = True, True, True, True
                    could_move_right = True
                elif(game.board.move_down(game.board.board)):
                    game.board.update_board()
                    game.board.add_tile(game.board.select_two_or_four(), game.board.select_random_empty_tile())
                    pygame.display.update()
                    #could_move_left, could_move_right, could_move_up, could_move_down = True, True, True, True
                    could_move_down = True
                else:
                    #print("Game over")
                    #try:
                    #    ge[x].fitness -=10
                    #except:
                    #    continue
                    nets.pop(x)
                    ge.pop(x)
                    games.pop(x)
                    print("GAME OVER, REMOVED GAME")
                    #time.sleep(5)



        # Logic to manually play
        '''game.draw_window()
        for event in pygame.event.get():
            if not could_move_left and not could_move_right and not could_move_up and not could_move_down:
                game.run = False
                pygame.quit()
                quit()
            if event.type == pygame.QUIT:
                game.run = False
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if(game.board.move_left(game.board.board)):
                        game.board.update_board()
                        game.board.add_tile(game.board.select_two_or_four(), game.board.select_random_empty_tile())
                        pygame.display.update()
                        could_move_up, could_move_down, could_move_right, could_move_left = True, True, True, True
                    else:
                        could_move_left = False
                if event.key == pygame.K_RIGHT:
                    if(game.board.move_right(game.board.board)):
                        game.board.update_board()
                        game.board.add_tile(game.board.select_two_or_four(), game.board.select_random_empty_tile())
                        pygame.display.update()
                        could_move_up, could_move_down, could_move_right, could_move_left = True, True, True, True
                    else:
                        could_move_right = False
                if event.key == pygame.K_UP:
                    if(game.board.move_up(game.board.board)):
                        game.board.update_board()
                        game.board.add_tile(game.board.select_two_or_four(), game.board.select_random_empty_tile())
                        pygame.display.update()
                        could_move_up, could_move_down, could_move_right, could_move_left = True, True, True, True
                    else:
                        could_move_up = False
                if event.key == pygame.K_DOWN:
                    if(game.board.move_down(game.board.board)):
                        game.board.update_board()
                        game.board.add_tile(game.board.select_two_or_four(), game.board.select_random_empty_tile())
                        pygame.display.update()
                        could_move_up, could_move_down, could_move_right, could_move_left = True, True, True, True
                    else:
                        could_move_down = False'''


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))

    stats = neat.StatisticsReporter()

    p.add_reporter(stats)

    winner = p.run(game_loop, 100)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
