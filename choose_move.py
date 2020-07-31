
import random
import json


def distance(node1, node2):
    return abs(node2["x"]-node1["x"]) + abs(node2["y"]-node1["y"])


FOOD_POINTS = 10
WALL_POINTS = -10**6
ENEMY_BODY = -10**4
SELF_BODY = -9*10**5
HEALTHIER_ENEMY_AURA = -20
AVAILABLE_MOVE_MAX_POINTS = 20
AVAILABLE_MOVE_MIN_POINTS = -3

DEBUG = True
DUMP_ON_ERROR = False


def handle_error(error_name: str, exception: Exception, data=None):
    print("An exception occured: ", error_name, exception)
    if DEBUG:
        print(exception.with_traceback())
    if DUMP_ON_ERROR:
        print("Object dump:", json.dumps(data))


def move(data):

    # Choose a random direction to move in
    possible_moves = ["up", "down", "left", "right"]
    choice = random.choice(possible_moves)
    shout = "Snecko eye"

    if data is None:
        return (choice, shout)

    board = build_board(data)
    # Notice that the board is actually set up to be indexed as board[y][x], not board[x][y]
    # We just ignore that and consistenly use [x][y]
    print("Initialized empty board")

    try:
        head = data["you"]["body"][0]
        self_x = head["x"]
        self_y = head["y"]
        print(f"Head pos: ({self_x}, {self_y})")
    except Exception as e:
        handle_error("Failed to get self position", e, data)
    try:
        try:
            get_snakes(data, board)
            print("Got impassible tiles")
        except Exception as e:
            handle_error("Failed to get impassible tiles", e, data)

        try:
            get_food(data, board, head)
            print("Got food tiles")
        except Exception as e:
            handle_error("Failed to get food tiles", e, data)

        try:
            get_available_move_bonus(data, board, head)
            print("Got available move bonus")
        except Exception as e:
            handle_error("Failed to get available move bonus", e, data)

        best_val = WALL_POINTS
        best_move = None
        # moves_on_board = list(possible_moves)
        if DEBUG:
            try:
                print_board(board, 5)
            except Exception as e:
                handle_error("Failed to print board (??)", e, data)

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
            # print(f"Possible moves: {[possible_moves]}")
            if moves_on_board != []:
                possible_moves = moves_on_board
        except Exception as e:
            handle_error("Failed to find best move", e, board)

        # print(f"Value = {best_val}")
        if best_val < -500:
            shout = "GG!"
        if choice is not None:
            choice = best_move

        if DEBUG:
            print_board(board, 6)

    except Exception as e:
        shout = "Failed to execute main move selection. Choosing randomly."
        handle_error("Failed to execute main move selection", e, data)
    finally:
        # print(shout)
        return (choice, shout)


def get_adjacent_in_board(board, node):
    x = node["x"]
    y = node["y"]
    coords = []
    if x > 0:
        coords.append({"x": x-1, "y": y})
    if x < len(board[0])-1:
        coords.append({"x": x+1, "y": y})
    if y > 0:
        coords.append({"x": x, "y": y-1})
    if y < len(board)-1:
        coords.append({"x": x, "y": y+1})
    # print(f"adjacent tiles: {coords}")
    return coords


def pathfind(node1, node2):
    x1 = node1["x"]
    x2 = node2["x"]
    y1 = node1["y"]
    y2 = node2["y"]

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


def get_food(data, board, self_node):
    for food in data["board"]["food"]:
        board[food["x"]][food["y"]] += FOOD_POINTS

        self_dist = distance(self_node, food)
        snake_dist = []
        for snake in data["board"]["snakes"]:
            if snake["id"] == data["you"]["id"]:
                continue
            snake_dist.append(distance(snake["body"][0], food))
        if min(snake_dist) > self_dist:
            print("Found an easily-eatable food")
            path = pathfind(self_node, food)
            for step in path:
                food_path_pts = (path.index(step) *
                                 FOOD_POINTS) // len(path) + 1
                board[step["x"]][step["y"]] += food_path_pts
                if DEBUG:
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
                    for coord in get_adjacent_in_board(board, snake["body"][0]):
                        board[coord["x"]][coord["y"]] += HEALTHIER_ENEMY_AURA
                        # print(f"Generated healthy enemy aura on ({coord})")
            except:
                print("Failed to generate aura around healthier enemy snake")

        for coords in snake["body"]:
            board[coords["x"]][coords["y"]] += points


def print_board(board, cell_width):
    print("Board:")
    for line in board:
        print([str(x).ljust((cell_width + 1) // 2).rjust(cell_width)
               for x in line])


def get_available_move_bonus(data, board, self_node):
    nodes = get_adjacent_in_board(board, self_node)
    max_moves = -10000
    min_moves = 10000
    MOVE_POINT_DIFFERENCE = AVAILABLE_MOVE_MAX_POINTS - AVAILABLE_MOVE_MIN_POINTS
    node_move_bonuses = [{"node": node, "move_bonus": -100} for node in nodes]
    for node_and_move_bonus in node_move_bonuses:
        node=node_and_move_bonus["node"]
        try:
            moves = count_nodes(board, -10, 50, node)
        except Exception as e:
            handle_error("dfs error", e, [board, -10, 50, node])
            moves = -100
        node_and_move_bonus["move_bonus"] = moves
        if DEBUG:
            print(f"Node {node} has a path of {moves} moves.")

        if moves > max_moves:
            max_moves = moves
        if moves < min_moves:
            min_moves = moves
    if DEBUG:
        print(f"Max moves: {max_moves}, Min moves: {min_moves}")
    for node_and_move_bonus in node_move_bonuses:
        node = node_and_move_bonus["node"]
        if min_moves == max_moves:
            move_points = 0
        else:
            move_points = AVAILABLE_MOVE_MIN_POINTS + \
                (node_and_move_bonus["move_bonus"] - min_moves) // (max_moves -
                                        min_moves) * MOVE_POINT_DIFFERENCE
        board[node["x"]][node["y"]] += move_points
        if DEBUG:
            print(f"Assigning {move_points} move points to node {node}")


def count_nodes(board, threshold, max_iterations, node):

    # Make search space
    visitable = []
    for row in board:
        visitable.append(
            [True if item > threshold else False for item in row])
    if not visitable[node["x"]][node["y"]]:
        return 0

    sum = 0
    to_visit = [node]
    # Search through the queue
    for i in range(max_iterations):
        # print(i)
        # for row in visitable:
        #     print(["x" if val else "." for val in row])
        if len(to_visit) < 1:
            break
        curr_node = to_visit.pop(0)
        visitable[curr_node["x"]][curr_node["y"]] = False
        sum += 1
        coords = get_adjacent_in_board(visitable, curr_node)
        for coord in coords:
            if visitable[coord["x"]][coord["y"]]:
                to_visit.append(coord)
    return sum


def build_board(data):
    try:
        x = [0 for _ in range(data["board"]["width"])]
        return [list(x) for _ in range(data["board"]["height"])]
    except Exception as e:
        shout = "Failed to build board. Assuming 11*11"
        handle_error(shout, e, data)
        return [list([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]) for _ in range(11)]


# if __name__ == "__main__":

#     count_nodes(*[[[-900000, 0, 0, 0, 0, 0, 0], [-900000, 0, 0, 0, 0, 0, 10], [-900000, 0, 0, -20, 0, 0, 0], [-900000, 0, -20, -10000, -20, 0, 10], [-900000,

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

    # board = build_board({"board":{"width":5, "height":5}})
    # for i in range(5):
    #     for j in range(5):
    #         board[i][j] = 10*i+j
    # print_board(board, 2)
