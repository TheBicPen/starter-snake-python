
import random


def distance(x1, y1, x2, y2):
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
        try:
            guaranteed_impassible(data, board)
            print("Got impassible tiles")
        except:
            print("Failed to get impassible tiles")
        try:
            get_food(data, board)
            print("Got food tiles")
        except:
            print("Failed to get food tiles")
        best_val = -10000
        best_move = None
        # moves_on_board = list(possible_moves)
        print("Board:")
        for line in board:
            print([str(x).ljust(2).rjust(4) for x in line])
        try:
            self_x = data["you"]["body"][0]["x"]
            self_y = data["you"]["body"][0]["y"]
            print(f"Head pos: ({self_x}, {self_y})")
            moves_on_board = []

            if self_x > 0:
                moves_on_board.append("left")
                val = board[self_x-1][self_y]
                print(f"Left val: {val}")
                if val > best_val:
                    best_val = val
                    best_move = "left"
            if self_x < len(board[0])-1:
                moves_on_board.append("right")
                val = board[self_x+1][self_y]
                print(f"Right val: {val}")
                if val > best_val:
                    best_val = val
                    best_move = "right"
            if self_y > 0:
                moves_on_board.append("up")
                val = board[self_x][self_y-1]
                print(f"Up val: {val}")
                if val > best_val:
                    best_val = val
                    best_move = "up"
            if self_y <= len(board)-1:
                moves_on_board.append("down")
                val = board[self_x][self_y+1]
                print("Down val: {val}")
                if val > best_val:
                    best_val = val
                    best_move = "down"
            print(f"Possible moves: {[possible_moves]}")
            if moves_on_board != []:
                possible_moves = moves_on_board
        except:
            print("Failed to find best move")

        print(f"Value = {best_val}")
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

        if choice is not None:
            choice = best_move

    except:
        shout = "Failed to execute main move selection. Choosing randomly."
    finally:
        print(shout)
        return (choice, shout)


def pathfind(x1, y1, x2, y2):
    x_min = min(x1,x2)
    x_max = max(x1,x2)
    y_min = min(y1,y2)
    y_max = max(y1,y2)
    coords = []
    for y in range(y_min+1,y_max+1):
        coords.append({"x": x1, "y":y})
    for x in range(x_min+1,x_max+1):
        coords.append({"x": x, "y":y2})
    return coords



def get_food(data, board, self_x, self_y):
    for food in data["board"]["food"]:
        board[food["x"]][food["y"]] += 10

        self_dist = distance(self_x, self_y, food["x"], food["y"])
        snake_dist = []
        for snake in data["board"]["snakes"]:
            if snake["id"] == data["you"]["id"]:
                continue
            snake_dist.append(distance(snake["body"][0]["x"], snake["body"][0]["y"],
                                       food["x"], food["y"]))
        if min(snake_dist) > self_dist:
            print("Found an easily-eatable food")
            for coord in pathfind(self_x, self_y, food["x"], food["y"]):
                board[coord["x"]][coord["y"]] += 1


def guaranteed_impassible(data, board):
    for snake in data["board"]["snakes"]:
        for coords in snake["body"][1:]:
            board[coords["x"]][coords["y"]] -= 100


def build_board(data):
    try:
        x = [0 for _ in range(data["board"]["width"])]
        return [list(x) for _ in range(data["board"]["height"])]
    except:
        shout = "Failed to build board. Assuming 11*11"
        print(shout)
        return [list([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]) for _ in range(11)]
