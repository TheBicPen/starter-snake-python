
import random


def distance(x1,y1,x2,y2):
    return abs(x2-x1) + abs(y2-y1)

def move(data):
        
    # Choose a random direction to move in
    possible_moves = ["up", "down", "left", "right"]
    choice = random.choice(possible_moves)
    shout = "Snecko eye"

    if data is None:
        return (choice, shout)
    
    board = build_board(data)
    print("Initialized empty board")
    try:
        guaranteed_impassible(data, board)
        print("Got impassible tiles")
        get_food(data, board)
        print("Got food tiles")

        self_x = data["you"]["body"][0]["x"]
        self_y = data["you"]["body"][0]["y"]

        best_val = -1000
        best_move = None
        # moves_on_board = list(possible_moves)
        try:
            moves_on_board = []
            if self_x > 0:
                moves_on_board.append("left")
                if board[self_x-1][self_y] > best_val:
                    best_val = board[self_x-1][self_y]
                    best_move = "left"
            if self_x < len(board[0]-1):
                moves_on_board.append("right")
                if board[self_x+1][self_y] > best_val:
                    best_val = board[self_x+1][self_y]
                    best_move = "right"
            if self_y > 0:
                moves_on_board.append("up")
                if board[self_x][self_y-1] > best_val:
                    best_val = board[self_x][self_y-1]
                    best_move = "up"
            if self_y <= len(board)-1:
                moves_on_board.remove("down")
                if board[self_x][self_y+1] > best_val:
                    best_val = board[self_x][self_y+1]
                    best_move = "down"
            if moves_on_board != []:
                possible_moves = moves_on_board
        except:
            print("failed to find best move")
                
        print(f"Value = {val}")
        # if val < 0:
        #     shout = "oh no"
        # if board[self_x-1][self_y] == val:
        #     choice = "left"
        # elif board[self_x+1][self_y] == val:
        #     choice = "right"
        # elif board[self_x][self_y-1] == val:
        #     choice = "down"
        # else:
        #     choice = "up"
        print(board)

        if choice is not None:
            choice = best_move

    except:
        shout = "Failed to execute main move selection. Choosing randomly."
    finally:
        print(shout)
        return (choice, shout)


def get_food(data, board):
    for food in data["board"]["food"]:
        board[food["x"]][food["y"]] += 5
    

def guaranteed_impassible(data, board):
    for snake in data["snakes"]:
        for coords in snake["body"][1:]:
            board[coords["x"]][coords["y"]] -= 20
    
    

def build_board(data):
    try:
        x = [0 for _ in range(data["board"]["width"])]
        return [list(x) for _ in range(data["board"]["height"])]
    except:
        shout = "Failed to build board. Assuming 11*11"
        print(shout)
        return [list([0,0,0,0,0,0,0,0,0,0,0]) for _ in range(11)]