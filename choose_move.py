
import random


def distance(x1, y1, x2, y2):
    return abs(x2-x1) + abs(y2-y1)


FOOD_POINTS = 10
WALL_POINTS = -10000
ENEMY_BODY = -1000
SELF_BODY = -9000
HEALTHIER_ENEMY_AURA = -20
AVAILABLE_MOVE_MAX_POINTS = 20
AVAILABLE_MOVE_MIN_POINTS = 0


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
        self_x = data["you"]["body"][0]["x"]
        self_y = data["you"]["body"][0]["y"]
        print(f"Head pos: ({self_x}, {self_y})")
    except:
        print("Failed to get self position")
    try:
        try:
            get_snakes(data, board)
            print("Got impassible tiles")
        except:
            print("Failed to get impassible tiles")

        try:
            get_food(data, board, self_x, self_y)
            print("Got food tiles")
        except:
            print("Failed to get food tiles")

        try:
            get_available_move_bonus(data, board, self_x, self_y)
            print("Got available move bonus")
        except:
            print("Failed to get available move bonus")

        best_val = WALL_POINTS
        best_move = None
        # moves_on_board = list(possible_moves)
        print("Board:")
        for line in board:
            print([str(x).ljust(2).rjust(5) for x in line])
        try:
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
                print(f"Down val: {val}")
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


def get_adjacent_in_board(board, x, y):
    coords = []
    if x > 0:
        coords.append({"x": x-1, "y": y})
    if x < len(board[0])-1:
        coords.append({"x": x+1, "y": y})
    if y > 0:
        coords.append({"x": x, "y": y-1})
    if y <= len(board)-1:
        coords.append({"x": x, "y": y+1})
    # print(f"adjacent tiles: {coords}")
    return coords


def pathfind(x1, y1, x2, y2):
    x_min = min(x1, x2)
    x_max = max(x1, x2)
    y_min = min(y1, y2)
    y_max = max(y1, y2)
    coords = []
    for y in range(y_min+1, y_max+1):
        coords.append({"x": x1, "y": y})
    for x in range(x_min+1, x_max+1):
        coords.append({"x": x, "y": y2})
    return coords


def get_food(data, board, self_x, self_y):
    for food in data["board"]["food"]:
        board[food["x"]][food["y"]] += FOOD_POINTS

        self_dist = distance(self_x, self_y, food["x"], food["y"])
        snake_dist = []
        for snake in data["board"]["snakes"]:
            if snake["id"] == data["you"]["id"]:
                continue
            snake_dist.append(distance(snake["body"][0]["x"], snake["body"][0]["y"],
                                       food["x"], food["y"]))
        if min(snake_dist) > self_dist:
            print("Found an easily-eatable food")
            path = pathfind(self_x, self_y, food["x"], food["y"])
            for step in path:
                food_path_pts = (path.index(step) *
                                 FOOD_POINTS) // len(path) + 1
                board[step["x"]][step["y"]] += food_path_pts
                print(f"Food path: ({step}), {food_path_pts}")


def get_snakes(data, board):
    for snake in data["board"]["snakes"]:
        if snake["id"] == data["you"]["id"]:
            points = SELF_BODY
        else:
            points = ENEMY_BODY

            # generate aura
            try:
                if snake["health"] >= data["you"]["health"]:
                    for coord in get_adjacent_in_board(board, snake["body"][0]["x"], snake["body"][0]["y"]):
                        board[coord["x"]][coord["y"]] += HEALTHIER_ENEMY_AURA
                        print(f"Generated healthy enemy aura on ({coord})")
            except:
                print("Failed to generate aura around healthier enemy snake")

        for coords in snake["body"]:
            board[coords["x"]][coords["y"]] += points


def get_available_move_bonus(data, board, self_x, self_y):
    nodes = get_adjacent_in_board(board, self_x, self_y)
    max_moves = -100
    min_moves = 10000
    MOVE_POINT_DIFFERENCE = AVAILABLE_MOVE_MAX_POINTS - AVAILABLE_MOVE_MIN_POINTS
    for node in nodes:
        moves = dfs(board, -10, 50, node["x"], node["y"])
        node["sum"] = moves
        if moves > max_moves:
            max_moves = moves
        if moves < min_moves:
            min_moves = moves
    print(f"Max moves: {max_moves}, Min moves: {min_moves}")    
    for node in nodes:
        move_points = AVAILABLE_MOVE_MIN_POINTS + (moves - min_moves) // (max_moves - min_moves) * MOVE_POINT_DIFFERENCE
        board[node["x"]][node["y"]] += move_points
        print(f"Assigning {move_points} move points to node {node}")

def dfs(board, threshold, max_iterations, x, y):

    node = {"x":x, "y":y, "sum":0}
    visitable = []
    for row in board:
        visitable.append(
            [True if item > threshold else False for item in row])
    # print(visitable)
    if not visitable[x][y]:
        return 0
    to_visit = [node]

    for i in range(max_iterations):
        # print(i)
        # for row in visitable:
        #     print(["x" if val else "." for val in row])
        if len(to_visit) < 1:
            break
        coords = get_adjacent_in_board(
            visitable, to_visit[0]["x"], to_visit[0]["y"])
        to_visit.pop(0)
        for coord in coords:
            if visitable[coord["x"]][coord["y"]]:
                visitable[coord["x"]][coord["y"]] = False
                node["sum"] += 1
                to_visit.append(coord)

    return node["sum"]
    

def build_board(data):
    try:
        x = [0 for _ in range(data["board"]["width"])]
        return [list(x) for _ in range(data["board"]["height"])]
    except:
        shout = "Failed to build board. Assuming 11*11"
        print(shout)
        return [list([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]) for _ in range(11)]

# if __name__ == "__main__":
#     print(dfs([[0, -1, 0, 0, 0, 0, 0, 0, 10, 0, 0],
# [0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
# [0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
# [0, -1, 0, 0, 0, 0, 0, 0, 10, 0, 0],
# [0, -1, 0, -9000, 0, 0, 0, 0, 0, 0, 0],
# [-1, -1, 0, -9000, 0, 0, 0, 0, 0, 0, 0],
# [0, 0, 0, -9000, 0, 0, 0, 0, 0, 0, 0],
# [0, 0, 0, -9000, 0, 0, -1000, -1000, -1000, -1000, -1000],
# [0, 0, 0, -9000, 0, -1000, -1000, 0, 0, -1000, -1000],
# [0, 0, 0, -9000, 10, -1000, 0, 0, 0, -1000, 0],
# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], -1, 20, 0, 2))
