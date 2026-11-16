import os
from collections import deque

os.system("")   # makes the colours work in the Windows terminal too

# ---------- Colours (ANSI codes) ----------
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"

# Each maze cell is drawn as 2 characters wide so the maze looks square
WALL_CELL = "\033[45m  " + RESET           # purple block
FLOOR_CELL = "\033[47m  " + RESET          # light grey floor
PLAYER_CELL = "\033[43;30;1m P" + RESET    # yellow block with a P
EXIT_CELL = "\033[42;30;1m E" + RESET      # green block with an E
PATH_CELL = "\033[46;30;1m *" + RESET      # cyan block (shortest path)


def clear_screen():
    print("\033[2J\033[H", end="")


def say(text, colour):
    """Prints a message in a colour."""
    print(colour + text + RESET)


def print_title():
    print(CYAN + BOLD + "╔══════════════════════════╗")
    print("║     MAZE ESCAPE GAME     ║")
    print("╚══════════════════════════╝" + RESET)


def get_maze(level_number):
    """Builds a fresh 2D list for the chosen level (0 means Level 1)."""
    maze = []
    for line in LEVELS[level_number]:
        maze.append(list(line))   # turn each text row into a list
    return maze


def print_maze(maze):
    """Prints the maze row by row inside a border, with colours."""
    total_cols = len(maze[0])
    print()
    print("  ╔" + "══" * total_cols + "╗")
    for row in maze:
        line = ""
        for cell in row:
            if cell == "#":
                line = line + WALL_CELL
            elif cell == "P":
                line = line + PLAYER_CELL
            elif cell == "E":
                line = line + EXIT_CELL
            elif cell == "*":
                line = line + PATH_CELL
            else:
                line = line + FLOOR_CELL
        print("  ║" + line + "║")
    print("  ╚" + "══" * total_cols + "╝")
    print()


def print_legend():
    print("  " + PLAYER_CELL + " you   " + EXIT_CELL + " exit   " + WALL_CELL + " wall   " + FLOOR_CELL + " path")


def play_game(level_number):
    maze = get_maze(level_number)
    total_rows = len(maze)
    total_cols = len(maze[0])
    row = 0   # player starts at row 0
    col = 0   # player starts at column 0
    moves = 0

    clear_screen()
    print_title()
    say("  Level " + str(level_number + 1) + " of " + str(len(LEVELS)), YELLOW)
    print("  Reach the exit! Use W (up), A (left), S (down), D (right).")
    print("  Type many keys at once, like DDSS. Type Q to go back to the menu.")
    print_legend()
    print_maze(maze)

    while True:
        keys = input("Enter move(s): ").upper()

        for key in keys:
            if key == " " or key == ",":
                continue  # ignore spaces and commas

            if key == "Q":
                return

            # Work out where the player WANTS to go
            new_row = row
            new_col = col
            if key == "W":
                new_row = row - 1
            elif key == "S":
                new_row = row + 1
            elif key == "A":
                new_col = col - 1
            elif key == "D":
                new_col = col + 1
            else:
                say("Invalid key '" + key + "'. Use W, A, S or D only.", YELLOW)
                continue

            # Check 1: is the new place outside the maze?
            if new_row < 0 or new_row >= total_rows or new_col < 0 or new_col >= total_cols:
                say("Cannot move outside the maze. Player stays at (" + str(row) + ", " + str(col) + ") | Moves: " + str(moves), RED)
                print_maze(maze)
                continue

            # Check 2: is there a wall?
            if maze[new_row][new_col] == "#":
                say("Wall ahead. Move blocked. Player stays at (" + str(row) + ", " + str(col) + ")", RED)
                say("Moves counted: " + str(moves), RED)
                print_maze(maze)
                continue

            # The move is valid, so update the maze
            reached_exit = (maze[new_row][new_col] == "E")
            maze[row][col] = "."
            maze[new_row][new_col] = "P"
            row = new_row
            col = new_col
            moves = moves + 1

            say("Player moved to (" + str(row) + ", " + str(col) + ") | Moves: " + str(moves), GREEN)
            print_maze(maze)

            if reached_exit:
                say("*** You escaped the maze! Total moves: " + str(moves) + " ***", GREEN + BOLD)
                if level_number + 1 < len(LEVELS):
                    print("Level complete! Use option 3 in the menu to go to the next level.\n")
                else:
                    say("Amazing! You finished all " + str(len(LEVELS)) + " levels!", GREEN + BOLD)
                return


def find_shortest_path(level_number):
    """Uses BFS (Breadth First Search) to find the shortest path from start to exit."""
    maze = get_maze(level_number)
    total_rows = len(maze)
    total_cols = len(maze[0])

    # Find the start and the exit
    start = (0, 0)
    end = (total_rows - 1, total_cols - 1)
    for r in range(total_rows):
        for c in range(total_cols):
            if maze[r][c] == "P":
                start = (r, c)
            if maze[r][c] == "E":
                end = (r, c)

    queue = deque()
    queue.append(start)
    visited = set()
    visited.add(start)
    came_from = {}  # remembers which cell we came from, to rebuild the path

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right

    while len(queue) > 0:
        current = queue.popleft()

        if current == end:
            break

        for d in directions:
            nr = current[0] + d[0]
            nc = current[1] + d[1]
            if nr < 0 or nr >= total_rows or nc < 0 or nc >= total_cols:
                continue
            if maze[nr][nc] == "#":
                continue
            if (nr, nc) in visited:
                continue
            visited.add((nr, nc))
            came_from[(nr, nc)] = current
            queue.append((nr, nc))

    if end not in came_from:
        say("No path found.", RED)
        return

    # Walk backwards from the exit to the start
    path = []
    cell = end
    while cell != start:
        path.append(cell)
        cell = came_from[cell]
    path.append(start)
    path.reverse()
    
    # Mark the path with * on the maze
    for cell in path:
        if maze[cell[0]][cell[1]] == ".":
            maze[cell[0]][cell[1]] = "*"

    clear_screen()
    print_title()
    say("  Level " + str(level_number + 1) + " - shortest path (cyan blocks)", YELLOW)
    print_maze(maze)
    print("Path:", path)
    say("Shortest path length: " + str(len(path) - 1) + " steps", CYAN + BOLD)
    print()


def choose_level(current_level):
    """Lets the player pick a level. Returns the new level number (0 means Level 1)."""
    print("Levels: 1 to " + str(len(LEVELS)) + " (bigger number = harder)")
    choice = input("Enter level number: ")
    if choice.isdigit() and 1 <= int(choice) <= len(LEVELS):
        say("Level " + choice + " selected.\n", GREEN)
        return int(choice) - 1
    say("Invalid level. Staying on Level " + str(current_level + 1) + ".\n", RED)
    return current_level


def main():
    current_level = 0   # start on Level 1
    clear_screen()
    while True:
        print_title()
        say("  Current level: " + str(current_level + 1), YELLOW)
        print("  1. Play the game")
        print("  2. Shortest path")
        print("  3. Choose level")
        print("  4. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            play_game(current_level)
        elif choice == "2":
            find_shortest_path(current_level)
        elif choice == "3":
            current_level = choose_level(current_level)
        elif choice == "4":
            say("Thanks for playing!", CYAN)
            break
        else:
            say("Invalid option. Please enter 1, 2, 3 or 4.\n", RED)


LEVELS = [
    # Level 1 (5 x 5)
    [
        "P..##",
        "##.##",
        "#...#",
        "#.###",
        "#...E",
    ],
    # Level 2 (7 x 7)
    [
        "P....#.",
        "####.#.",
        "...#.#.",
        ".#.#.#.",
        ".#.#...",
        ".#.###.",
        ".#....E",
    ],
    # Level 3 (7 x 7)
    [
        "P..#...",
        "##.#.#.",
        "...#.#.",
        ".###.##",
        ".#.....",
        ".#####.",
        "......E",
    ],
    # Level 4 (7 x 7)
    [
        "P#.....",
        ".#.#.#.",
        ".#.#.#.",
        ".###.#.",
        ".....#.",
        "######.",
        "......E",
    ],
    # Level 5 (9 x 9)
    [
        "P..#.....",
        "##.#.#.##",
        ".#.#.#...",
        ".#.#####.",
        ".#.......",
        ".#######.",
        "...#.....",
        ".###.####",
        "........E",
    ],
    # Level 6 (9 x 9)
    [
        "P........",
        "########.",
        ".......#.",
        ".#.#####.",
        ".#.#...#.",
        ".#.#.#.#.",
        ".#.#.#...",
        ".#.#.####",
        ".#......E",
    ],
    # Level 7 (9 x 9)
    [
        "P#.#.....",
        ".#.#.#.#.",
        ".#.#.#.#.",
        ".#.#.#.#.",
        ".#...#.#.",
        ".#####.#.",
        "...#...#.",
        "##.#.###.",
        ".....#..E",
    ],
    # Level 8 (11 x 11)
    [
        "P..#.......",
        "##.#.#.###.",
        "...#.....#.",
        ".#.#####.##",
        "...#...#...",
        ".###.#.###.",
        ".....#.#...",
        "######.#.#.",
        ".....#.#.#.",
        ".###.#.#.#.",
        "...#.....#E",
    ],
    # Level 9 (11 x 11)
    [
        "P..#...#...",
        "##.#.#.#.#.",
        ".#.#.#...#.",
        ".#.#####.#.",
        "...#...#...",
        ".#.#.#.#.#.",
        ".#.#.#...#.",
        ".#.#.#####.",
        ".#.#...#.#.",
        ".#.###.#.#.",
        ".......#..E",
    ],
    # Level 10 (11 x 11)
    [
        "P#.........",
        ".#.#######.",
        "...#.......",
        "####.######",
        "...#.#.#...",
        ".#.#.#.#.#.",
        "...#.#...#.",
        ".###.#####.",
        ".#...#.....",
        ".#.###.#.#.",
        ".......#..E",
    ],
    # Level 11 (13 x 13)
    [
        "P#.....#.....",
        ".#.###.#.###.",
        "...#.#...#.#.",
        "####.#.###.#.",
        ".......#...#.",
        ".###.###.#.#.",
        "...#.#...#.#.",
        "##.#.#.###.#.",
        "...#.#.#.#...",
        ".#####.#.####",
        ".....#.#.....",
        ".#.#.#.###.#.",
        "...#.......#E",
    ],
    # Level 12 (13 x 13)
    [
        "P..#.....#...",
        "##.#.###.#.#.",
        "...#.#...#.#.",
        ".###.#.#.###.",
        ".#.....#.#...",
        ".###.#.#.#.#.",
        "...#.#.#.#.#.",
        "##.#.#.#.#.#.",
        ".#.#.#.#.....",
        ".#.#.#.#####.",
        "...#.#...#.#.",
        ".#.#####.#.#.",
        ".........#..E",
    ],
    # Level 13 (13 x 13)
    [
        "P..#.....#...",
        "##.#.#.#.###.",
        ".#.#.........",
        ".#.#.#######.",
        ".#.#.#.#...#.",
        ".#.#.#.#.#.#.",
        ".#...#...#.#.",
        ".#####.###.#.",
        ".#...#...#...",
        ".#.#.###.####",
        "...#...#.#...",
        ".#.###.#.#.#.",
        ".....#.....#E",
    ],
    # Level 14 (15 x 15)
    [
        "P........#.....",
        "########.#.####",
        ".......#.#.....",
        ".###.###.#####.",
        "...#.....#...#.",
        "##.#######.#.#.",
        "...#.....#.#...",
        ".###.###.#.###.",
        ".....#.....#.#.",
        "######.#####.#.",
        ".#...#.........",
        ".#.#.#.########",
        "...#.#...#.....",
        ".###.###.###.#.",
        "..............E",
    ],
    # Level 15 (15 x 15)
    [
        "P....#.........",
        "####.#.#####.#.",
        "...#.#.#.#...#.",
        "##.#.#.#.#.###.",
        "...#.#...#.#.#.",
        ".###.#.###.#.#.",
        "...#.......#...",
        ".#.#######.#.##",
        ".#...........#.",
        ".#############.",
        ".....#.........",
        "####.#########.",
        ".....#.....#...",
        ".#####.###.#.#.",
        ".............#E",
    ],
    # Level 16 (15 x 15)
    [
        "P#.......#...#.",
        ".#.#####.#.#.#.",
        ".#.#.#...#.#.#.",
        ".#.#.#.###.#.#.",
        ".#.#...#...#...",
        ".#.#.###.#####.",
        "...#...#.....#.",
        "######.###.#.#.",
        "...#.#.......#.",
        ".#.#.#########.",
        ".#...#.....#...",
        ".###.#.###.#.#.",
        ".....#.#...#...",
        ".###.#.#.###.#.",
        "...#...#......E",
    ],
    # Level 17 (17 x 17)
    [
        "P..#.......#.....",
        "##.#####.#.#.###.",
        ".#.....#.#.#...#.",
        ".#####.#.#.###.#.",
        ".....#...#.#...#.",
        ".###.#####.#.###.",
        "...#.....#.#.#...",
        "##.#.#.#.#.#.####",
        ".#.....#...#.....",
        ".###.#.#####.###.",
        ".#...#...#...#...",
        ".#.#.###.#####.#.",
        ".#.#...#.#.....#.",
        ".#.#.#.#.#.#####.",
        ".#...#...#.#.#...",
        ".###.#####.#.#.##",
        "...........#....E",
    ],
    # Level 18 (17 x 17)
    [
        "P#.....#.......#.",
        ".#.###.#.###.#.#.",
        ".#...#.#.#...#...",
        ".###.#.#.#.#####.",
        ".#...#.#.#.#...#.",
        ".#.###.#.#.#.###.",
        ".#.#.#.#.#.....#.",
        ".#.#.#.###.###.#.",
        "...#.#...#...#...",
        "####.###.#.#.####",
        ".........#.......",
        ".#####.#.#.#####.",
        ".#...#...#...#...",
        ".#.#.#########.#.",
        ".#.#.#.........#.",
        ".#.#.#.#########.",
        "...#............E",
    ],
    # Level 19 (17 x 17)
    [
        "P#...#...#.......",
        ".#.#.###.#.#####.",
        ".#.#...#...#.....",
        ".#.#.#.###.#.###.",
        "...#.#...#.#.#.#.",
        "####.###.#.#.#.#.",
        ".....#...#...#...",
        ".###.#.###.###.##",
        "...#...#.....#...",
        "##.#######.#.###.",
        ".#...#.....#...#.",
        ".###.#.#####.###.",
        ".#...#.#.....#...",
        ".#.###.#.#####.##",
        "...#...#.........",
        ".###.###.#######.",
        ".....#..........E",
    ],
    # Level 20 (19 x 19)
    [
        "P#.................",
        ".#####.###.#######.",
        ".#...#.#...#...#...",
        ".#.#.###.###.#.#.##",
        ".#.#.....#...#...#.",
        ".#.#######.#####.#.",
        "...#.......#...#.#.",
        "####.#.###.#.#.#.#.",
        "...#.#.#.#.#.#...#.",
        ".#.#.#.#.#.#.#####.",
        ".#...#.#.#.#.......",
        "##.###.#.#.#######.",
        "...#...#.#.#.......",
        ".#.#.###.#.#.######",
        ".#...#.....#.#.....",
        ".#####.#####.###.#.",
        "...#...#...#.#.....",
        ".#.###.#.#.#.#.#.#.",
        ".#.......#.....#..E",
    ],
    # Level 21 (19 x 19)
    [
        "P#.#.....#...#.....",
        ".#.#.#.#.#.#.#####.",
        ".#...#.#...#...#...",
        ".#####.#######.#.#.",
        ".....#...#.#...#.#.",
        ".###.###.#.#.###.#.",
        ".#...#...#...#...#.",
        ".#.###.###.#####.#.",
        ".#.....#...#...#.#.",
        ".#######.###.#.#.#.",
        ".......#.#...#...#.",
        ".###.#.#.#.#######.",
        ".....#.#.#.....#...",
        ".#####.#.#.###.#.##",
        ".........#.#...#...",
        "####.###.###.###.#.",
        "...#.#.....#...#...",
        ".#.#.###.#.###.#.##",
        ".#.......#.....#..E",
    ],
    # Level 22 (19 x 19)
    [
        "P....#.#...........",
        "####.#.#.#####.###.",
        "...#.#...#...#.#...",
        ".#.#.#####.#.#.#.##",
        ".#...#...#.#.#.#.#.",
        ".#####.#.#.#.#.#.#.",
        ".....#.#...#...#...",
        "####.#.#####.#.####",
        "...#.#...#.#.#.....",
        ".###.###.#.#.#.###.",
        ".....#...#...#.#...",
        ".#####.###.###.#.#.",
        "...#...#...#.....#.",
        "##.#.#.#.#####.#.#.",
        ".....#.#...#...#...",
        ".#####.###.#.###.##",
        "...#...#...#.#...#.",
        "##.#.###.#.#.#.###.",
        ".....#.......#....E",
    ],
    # Level 23 (21 x 21)
    [
        "P#...........#.......",
        ".#.###.#####.#.#.####",
        ".#.#...#...#.#.#.....",
        ".###.###.#.#.#.#####.",
        ".....#.......#...#...",
        "######.###########.##",
        "...#...#.........#...",
        ".###.###.#.#####.#.#.",
        ".....#...#.#...#.#.#.",
        ".#.#.#.###.#.###.#.#.",
        ".#...#.....#.#...#.#.",
        ".#######.#.#.#.#####.",
        "...#.....#.#.........",
        "##.#.#####.#####.###.",
        "...#...#...#.....#.#.",
        ".#######.###.###.#.#.",
        ".#.....#.....#.#.....",
        ".#.###.###.###.#.#.##",
        ".#...#...#.....#.#.#.",
        ".###.###.#######.#.#.",
        ".....#...........#..E",
    ],
    # Level 24 (21 x 21)
    [
        "P#...........#.......",
        ".#######.###.#####.#.",
        ".#.......#.#.....#.#.",
        ".#.###.###.#####.###.",
        ".#.......#.....#.#...",
        ".#.#####.#.###.#.#.##",
        ".#.#.....#.......#...",
        ".###.###.#.#.#######.",
        "...#.....#.#.........",
        "##.###.#.#.###.#####.",
        ".#...#.#.#...#.#.....",
        ".###.#.#.###.#.#.####",
        ".#...#.#.#.#.#.#.#...",
        ".#.#####.#.#.#.#.###.",
        "...#.....#...#...#...",
        ".###.#####.###.#.#.##",
        "...#.#...#.....#.#...",
        "##.#.#.#.#######.#.#.",
        ".#.#.#.#.......#.#.#.",
        ".#.#.#.###.#.#.#.###.",
        ".....#...#...#......E",
    ],
    # Level 25 (21 x 21)
    [
        "P....#.#.............",
        "####.#.#.###.########",
        "...#.#...#...#.......",
        ".#.#.#.###.#.#.#####.",
        ".#...#...#.#...#...#.",
        ".#######.#.#.###.#.#.",
        ".......#.#...#...#...",
        "######.#######.#####.",
        ".....#.......#...#...",
        ".#.#.#######.###.#.#.",
        ".#.#.#.....#.#...#.#.",
        ".#.###.###.#.#.###.#.",
        ".#.....#.#...#.......",
        ".#######.#####.#.###.",
        "...#.....#.......#.#.",
        "##.#####.#.###.###.#.",
        "...#...#.....#.#.....",
        ".###.#.#.#####.#.####",
        ".#...#.#.....#.#.....",
        ".#.###.#.###.#.#####.",
        "...#.....#..........E",
    ],
]

main()