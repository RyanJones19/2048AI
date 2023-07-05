board = [[16,16,0,2],
        [4,4,4,0],
        [4,2,2,2],
        [2,2,4,2]]


for row in board:
    print(row)

def move_left(board):
    changed = False
    for row in board:
        old_row = row[:]
        row[:] = [tile for tile in row if tile != 0] + [0] * row.count(0)
        for tile in range(len(row) - 1):
            if row[tile] == row[tile + 1]:
                row[tile] *= 2
                row[tile + 1] = 0

        row[:] = [tile for tile in row if tile != 0] + [0] * row.count(0)
        if row != old_row:
            changed = True
    return board, changed


def move_right(board):
    changed = False
    board_reversed = [row[::-1] for row in board]
    board_reversed, changed = move_left(board_reversed)
    board = [row[::-1] for row in board_reversed]
    return board, changed


def move_up(board):
    changed = False
    board_transposed = list(map(list, zip(*board)))
    board_transposed, changed = move_left(board_transposed)
    board = list(map(list, zip(*board_transposed)))
    return board, changed

def move_down(board):
    changed = False
    board_transposed_reversed = [row[::-1] for row in list(map(list, zip(*board)))]
    board_transposed_reversed, changed = move_left(board_transposed_reversed)
    board = list(map(list, zip(*[row[::-1] for row in board_transposed_reversed])))
    return board, changed

print("_________________________")
board, changed = move_down(board)
for row in board:
    print(row)
print(changed)  
