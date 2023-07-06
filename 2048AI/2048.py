import pygame
import neat
import time
import random
import os
import math
import copy
pygame.font.init()

# Set pixel values for the game window
WIN_WIDTH = 1000
WIN_HEIGHT = 1000
TILE_WIDTH = 28
TILE_HEIGHT = 32

# Load images
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

# Create a dictionary that maps each tile to its position on the board (pixel values)
for i in range(16):
    row = i // 4
    col = i % 4
    x = 28 + col * 242
    y = 32 + row * 242
    position_map[str(i+1)] = {"row": row, "col": col, "x": x, "y": y}

# Create a dictionary that maps each tile to its corresponding image
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
        # Tile class takes in value, row, and col
        # 0 represents an empty tile
        # Set the coordinates of each tile on the board
        # 4*i+j+1 represents the tile number, done like this because of the 2D list
        self.board = [[Tile(0, position_map[str(4*i+j+1)]["x"], position_map[str(4*i+j+1)]["y"]) for j in range(4)] for i in range(4)]
        for row in self.board:
            for tile in row:
                tile.draw(self.win)
        # Add two 2 or 4 tiles to random places on the board
        random_starting_tiles = random.sample(range(1, 17), 2)
        self.add_tile(self.select_two_or_four(), random_starting_tiles[0])
        self.add_tile(self.select_two_or_four(), random_starting_tiles[1])

    def select_two_or_four(self):
        return random.choice([2, 4])

    def print_board(self):
        for row in self.board:
            for tile in row:
                print(tile.value, end=" ")
            print()
        #time.sleep(2)


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

    def do_move(self):
        self.update_board()
        self.add_tile(self.select_two_or_four(), self.select_random_empty_tile())
        pygame.display.update()

    # Function to draw the game board
    def draw(self):
        self.win.blit(BOARD_IMAGE, (0, 0))

    # Function to move the tiles left
    # Returns if the board changed and the number of merges we made
    # First finds all zeros in a row and moves them to the end
    # If the new row is different from the old row, we know the board changed
    # Then, we check if two adjacent tiles are the same and merge them
    # We then move all zeros to the end again since tiles have been merged
    def move_left(self, board):
        changed = False
        merged_count = 0

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
                    merged_count += 1
                    changed = True
            zeros = [tile for tile in row if tile.value == 0]
            row[:] = [tile for tile in row if tile.value != 0] + zeros

        return changed, merged_count

    # Function to move right, to move right we reverse the board, move left, then reverse it back
    def move_right(self, board):
        reversed_board = [row[::-1] for row in board]
        changed, merged_count = self.move_left(reversed_board)
        self.board = [row[::-1] for row in reversed_board]
        return changed, merged_count

    # Function to move up, to move up we transpose the board, move left, then transpose it back
    def move_up(self, board):
        # Zip function transposes the board by taking the first element of each row and making it a new row, * operator unpacks the list
        transposed_board = list(map(list, zip(*board)))
        changed, merged_count = self.move_left(transposed_board)
        self.board = list(map(list, zip(*transposed_board)))
        return changed, merged_count

    # Function to move down, to move down we transpose the board, move right, then transpose it back
    def move_down(self, board):
        reversed_transposed_board = list(map(list, zip(*board[::-1])))
        changed, merged_count = self.move_left(reversed_transposed_board)
        self.board = list(map(list, zip(*reversed_transposed_board)))[::-1]
        return changed, merged_count

    # Function to use when a move failed, try all moves in below order
    def try_all_moves(self, board):
        if self.move_left(board) or self.move_right(board) or self.move_up(board) or self.move_down(board):
            self.update_board()
            self.add_tile(self.select_two_or_four(), self.select_random_empty_tile())
            pygame.display.update()
            return True
        else:
            return False

    # Try moves in the "suggested order" from the NN output
    def try_next_move(self, board, suggested_order):
        for move in suggested_order:
            if move == 0:
                changed, _ = self.move_left(board)
                if changed:
                    return True
            elif move == 1:
                changed, _ = self.move_right(board)
                if changed:
                    return True
            elif move == 2:
                changed, _ = self.move_up(board)
                if changed:
                    return True
            elif move == 3:
                changed, _ = self.move_down(board)
                if changed:
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
        zeros = 1
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
        print("Smoothness was: ", smoothness)
        return smoothness

    def calculate_board_state_fitness(self, board):
        fitness = 0
        positional_weights = [[16,15,14,13],[9,10,11,12],[8,7,6,5],[4,3,2,1]]
        for row_position, row in enumerate(board):
            for tile_position, tile in enumerate(row):
                fitness += tile.value * positional_weights[row_position][tile_position]
        print("Fitness added was: ", fitness)
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
    max_tile = 0

    nets = []
    ge = []
    games = []

    # Create a list of genomes, neural networks and games
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        game = Game()
        games.append(game)
        g.fitness = 0
        ge.append(g)

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        print("Number of remaining games in species: ", len(games))
        if len(games) == 0:
            run = False
            print("MAX TILE THIS GAME:", max_tile)
            time.sleep(5)
            break
        for x, game in enumerate(games):
            print("GAME NUMBER: ", x)
            print("REMAINING GAMES: ", len(ge))
            game.draw_window()
            # Every time we make a move, add to fitness
            ge[x].fitness += 500
            # Get the output from the neural network
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
                ge[x].fitness = ge[x].fitness * 2
                print(max_tile)

            if board_max_tile >= 512:
                print("Game Number: ", x)
                print("CURRENT FITNESS: ", ge[x].fitness)
                game.board.print_board()

            # create a new list containing the values 0 through 3 ordered based on the output index list
            # for example if index 2 is largest and index 1 is second largest the list would be [2,1,0,3]
            # if multiple values are the same randomize the order of the same values
            suggested_moves = sorted(range(len(output)), key=lambda k: (output[k], random.random()), reverse=True)
            print(suggested_moves)
            max_index = suggested_moves[0]

            if max_index == 0:
                print("Trying to move left...")
                could_move_left, num_merges = game.board.move_left(game.board.board)

                if could_move_left:
                    try:
                        print("Moved left and merged ", num_merges, " tiles")
                        ge[x].fitness += game.board.calculate_board_state_fitness(game.board.board) * num_merges
                    except:
                        continue
                    game.board.do_move()
                else:
                    print("Tried to move left but couldn't")
                    ge[x].fitness -= 100000
                    game.board.print_board()

                    # Attempt to move the next best direction if recommended failed
                    if game.board.try_next_move(game.board.board, suggested_moves):
                        game.board.do_move()
                    # If we can move no direction then the game is over and remove high fitness
                    else:
                        ge[x].fitness -= 500000
                        nets.pop(x)
                        ge.pop(x)
                        games.pop(x)
                        print("GAME OVER, REMOVED GAME")

            elif max_index == 1:
                print("Trying to move right...")
                could_move_right, num_merges = game.board.move_right(game.board.board)

                if could_move_right:
                    try:
                        print("Moved right and merged ", num_merges, " tiles")
                        ge[x].fitness += game.board.calculate_board_state_fitness(game.board.board) * num_merges
                    except:
                        continue
                    game.board.do_move()
                else:
                    print("Tried to move right but couldn't")
                    ge[x].fitness -= 100000
                    game.board.print_board()

                    # Attempt to move the next best direction if recommended failed
                    if game.board.try_next_move(game.board.board, suggested_moves):
                        game.board.do_move()
                    # If we can move no direction then the game is over and remove high fitness
                    else:
                        ge[x].fitness -= 500000
                        nets.pop(x)
                        ge.pop(x)
                        games.pop(x)
                        print("GAME OVER, REMOVED GAME")

            elif max_index == 2:
                print("Trying to move up...")
                could_move_up, num_merges = game.board.move_up(game.board.board)

                if could_move_up:
                    try:
                        print("Moved up and merged ", num_merges, " tiles")
                        ge[x].fitness += game.board.calculate_board_state_fitness(game.board.board) * num_merges
                    except:
                        continue
                    game.board.do_move()
                else:
                    print("Tried to move up but couldn't")
                    ge[x].fitness -= 100000
                    game.board.print_board()

                    # Attempt to move the next best direction if recommended failed
                    if game.board.try_next_move(game.board.board, suggested_moves):
                        game.board.do_move()
                    # If we can move no direction then the game is over and remove high fitness
                    else:
                        ge[x].fitness -= 500000
                        nets.pop(x)
                        ge.pop(x)
                        games.pop(x)
                        print("GAME OVER, REMOVED GAME")
            elif max_index == 3:
                print("Trying to move down...")
                could_move_down, num_merges = game.board.move_down(game.board.board)

                if could_move_down:
                    try:
                        print("Moved down and merged ", num_merges, " tiles")
                        ge[x].fitness += game.board.calculate_board_state_fitness(game.board.board) * num_merges
                    except:
                        continue
                    game.board.do_move()
                else:
                    print("Tried to move down but couldn't")
                    ge[x].fitness -= 100000
                    game.board.print_board()

                    # Attempt to move the next best direction if recommended failed
                    if game.board.try_next_move(game.board.board, suggested_moves):
                        game.board.do_move()
                    # If we can move no direction then the game is over and remove high fitness
                    else:
                        ge[x].fitness -= 500000
                        nets.pop(x)
                        ge.pop(x)
                        games.pop(x)
                        print("GAME OVER, REMOVED GAME")
            else:
                ge[x].fitness -= 1000000
                nets.pop(x)
                ge.pop(x)
                games.pop(x)
                print("GAME OVER, REMOVED GAME")
                time.sleep(5)


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
