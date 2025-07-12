import math
from copy import deepcopy
from collections import deque
from flask import Flask, request, jsonify
import threading
import uuid


class PentominoSolverAPI:
    def __init__(self):
        self.app = Flask(__name__)
        self.sessions = {}

        @self.app.route('/sessions', methods=['POST'])
        def create_session():
            try:
                data = request.json
                session_id = str(uuid.uuid4())
                grid_width = data['grid_width']
                grid_height = data['grid_height']
                pentomino_letters = data['pentomino_letters']
                exclusions = data.get('exclusions', [])
                
                solver = PentominoSolver(grid_width, grid_height, pentomino_letters, exclusions)
                self.sessions[session_id] = {
                    'solver': solver,
                    'solving_thread': None
                }
                return jsonify({'session_id': session_id}), 201
            except Exception as e:
                return jsonify({'error': str(e)}), 400

        @self.app.route('/sessions/<session_id>/solve', methods=['POST'])
        def solve(session_id):
            if session_id not in self.sessions:
                return jsonify({'error': 'Session not found'}), 404

            session = self.sessions[session_id]
            solver = session['solver']
            
            if session['solving_thread'] and session['solving_thread'].is_alive():
                return jsonify({'message': 'Solver is already running'}), 200

            def solving_task():
                try:
                    solver.solve()
                except Exception as e:
                    print(f"Error in solving thread: {e}")

            solving_thread = threading.Thread(target=solving_task)
            session['solving_thread'] = solving_thread
            solving_thread.start()

            return jsonify({'message': 'Solver started'}), 200

        @self.app.route('/sessions/<session_id>/progress', methods=['GET'])
        def progress(session_id):
            if session_id not in self.sessions:
                return jsonify({'error': 'Session not found'}), 404

            session = self.sessions[session_id]
            solver = session['solver']

            return jsonify({
                'grid': solver.last_attempt,
                'total_solutions_evaluated': solver.total_solutions_evaluated,
                'solved': bool(solver.solutions)
            }), 200

        @self.app.route('/sessions/<session_id>', methods=['DELETE'])
        def delete_session(session_id):
            if session_id in self.sessions:
                del self.sessions[session_id]
                return jsonify({'message': 'Session deleted'}), 200
            return jsonify({'error': 'Session not found'}), 404

    def run(self, host='0.0.0.0', port=5000):
        self.app.run(host=host, port=port)

class PentominoSolver:
    def __init__(self, grid_width, grid_height, pentomino_letters, exclusions, grid: list[list[str]] = None):
        self.total_solutions_evaluated = 0
        if grid_width <= 0 or grid_height <= 0:
            raise ValueError("Grid dimensions must be positive ")


        # Initialize the grid with '.'
        self.grid = [['.' for _ in range(grid_width)] for _ in range(grid_height)]
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.exclusions = exclusions
        used_letters = {}
        for (r, c) in exclusions:
            self.grid[r][c] = 'x'

        if grid:
            for r, row in enumerate(grid):
                for c, cell in enumerate(row):
                    if cell == 0:
                        cell = '.'
                    if cell not in ['.', 'x'] + [letter.upper() for letter in pentomino_letters]:
                        raise ValueError("Invalid grid cell")
                    if self.grid[r][c] == 'x':
                        continue
                    self.grid[r][c] = cell

        for r, row in enumerate(self.grid):
            for c, cell in enumerate(row):
                letter = used_letters.setdefault(cell, 0)
                used_letters[cell] = letter + 1

        for letter, count in used_letters.items():
            if letter == 'x':
                continue
            # All placed letters should have 5x the number of letters in the grid.
            # Remaining spacess should also be a multiple of 5x.
            if count % 5 != 0:
                raise ValueError("Invalid grid: Not enough cells")

        
        self.last_attempt = deepcopy(self.grid)
        self.solutions = []
        self.pentomino_shapes_dict = self.pentomino_shapes()

        # Initialize the grid. Then validate the grid is valid.
        for space in self.find_contiguous_spaces(self.grid):
            if len(space) < 5:
                raise ValueError("Has no contiguous spaces < 5")

        for letter in [ letter.upper() for letter in pentomino_letters]:
            if letter not in self.pentomino_shapes_dict:
                raise ValueError(f"Invalid pentomino letter: {letter}")

        pentomino_letters = [letter.upper() for letter in pentomino_letters if letter not in used_letters.keys()]
        self.pentomino_letters = self.sort_letters(pentomino_letters)

    def sort_letters(self, letters):
        # This is a critical optimization. It is faster to run the search with fewer
        # combinations first, then work your way up to lettes with the largest number
        # of shapes. The program runtime can be hours when starting with F and seconds
        # when starting with letters like X or I.
        return sorted(letters, key=lambda letter: len(self.pentomino_shapes_dict[letter]))
        
        
    def pentomino_shapes(self):
        """Generate the pentomino shapes using predefined configurations."""
        shapes = dict()
        shapes['F'] = self.get_all_shapes([(0, 1), (1, 0), (1, 1), (1, 2), (2, 2)], flip=True)
        shapes['L'] = self.get_all_shapes([(0, 0), (1, 0), (2, 0), (3, 0), (0, 1)])
        shapes['I'] = self.get_all_shapes([(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)])
        shapes['P'] = self.get_all_shapes([(0, 0), (1, 0), (2, 0), (0, 1), (1, 1)])
        shapes['N'] = self.get_all_shapes([(0, 1), (1, 0), (1, 1), (2, 0), (3, 0)])
        shapes['T'] = self.get_all_shapes([(1, 0), (1, 1), (1, 2), (0, 2), (2, 2)])
        shapes['U'] = self.get_all_shapes([(0, 0), (1, 0), (2, 0), (0, 1), (2, 1)])
        shapes['V'] = self.get_all_shapes([(0, 0), (0, 1), (0, 2), (1, 0), (2, 0)])
        shapes['W'] = self.get_all_shapes([(0, 0), (1, 0), (1, 1), (2, 1), (2, 2)])
        shapes['X'] = self.get_all_shapes([(0, 1), (1, 1), (2, 1), (1, 0), (1, 2)])
        shapes['Y'] = self.get_all_shapes([(0, 0), (0, 1), (0, 2), (0, 3), (1, 2)])
        shapes['Z'] = self.get_all_shapes([(2, 0), (2, 1), (1, 1), (0, 1), (0, 2)])
        return shapes

    def get_all_shapes(self, base_shape, flip=False):
        def rotate_point(x, y):
            """Rotate a point 90 degrees clockwise."""
            return y, -x
    
        def flip_horizontal(x, y):
            """Flip a point horizontally."""
            return -x, y
    
        def normalize(shape):
            """Shift the shape so its origin is at (0, 0)."""
            min_x = min(x for x, y in shape)
            min_y = min(y for x, y in shape)
            return sorted((x - min_x, y - min_y) for x, y in shape)
    
        transformations = set()
    
        # Generate all rotations and flips
        for _ in range(4):
            base_shape = normalize([rotate_point(x, y) for x, y in base_shape])
            transformations.add(tuple(base_shape))

            if flip:
                flipped_shape = normalize([flip_horizontal(x, y) for x, y in base_shape])
                transformations.add(tuple(flipped_shape))
    
        return [list(shape) for shape in transformations]

    def get_shapes(self, letter):
        return self.pentomino_shapes_dict[letter]

    def print_grid(self, current_grid=None):
        if current_grid is None:
            current_grid = self.grid
        for row in current_grid:
            print(' '.join(row))
        print()

    def print_shapes(self):
        for l in self.pentomino_shapes_dict.keys():
            for s in self.pentomino_shapes_dict[l]:
                self.print_pentomino(s, l)
                print()


    def print_pentomino(self, shape, letter):
        """
        Prints a pentomino shape on a grid.
        
        Parameters:
            shape (list of tuples): List of (x, y) relative coordinates for the shape.
            letter (str): The letter to represent the pentomino.
        """
        # Determine dynamic grid dimensions based on the shape
        min_x, min_y, max_x, max_y = 0, 0, 0, 0
        for x, y in shape:
            if x < min_x:
                min_x = x
            if y < min_y:
                min_y = y
            if x > max_x:
                max_x = x
            if y > max_y:
                max_y = y

        grid_width = max_x - min_x + 1
        grid_height = max_y - min_y + 1

        temp_grid = [['.' for _ in range(grid_width)] for _ in range(grid_height)]
        x = min_x
        y = min_y
        while (x <= max_x and y <= max_y + 1):
            if (x, y) in shape:
                temp_grid[y - min_y][x - min_x] = letter
            if x == max_x + 1:
                y += 1
                x = min_x
            else:
                x += 1

        # Print the grid
        for row in temp_grid:
            print(' '.join(row))

    def is_valid_placement(self, shape, x, y, current_grid):
        for dx, dy in shape:
            nx, ny = x + dx, y + dy
            # Check bounds
            if nx < 0 or ny < 0 or nx >= self.grid_width or ny >= self.grid_height:
                return False
            # Check exclusions and existing placements
            if current_grid[ny][nx] != '.':
                return False
        return True

    def place_pentomino(self, shape, x, y, letter, current_grid):
        """
        Place a pentomino on the grid.
        :param shape: List of relative (dx, dy) positions for the pentomino.
        :param x: Top-left x-coordinate of placement.
        :param y: Top-left y-coordinate of placement.
        :param letter: Letter of the pentomino.
        """
        for dx, dy in shape:
            nx, ny = x + dx, y + dy
            self.grid[ny][nx] = letter

    def remove_pentomino(self, shape, x, y, current_grid):

        for dx, dy in shape:
            nx, ny = x + dx, y + dy
            if current_grid[ny][nx] == '.':
                raise ValueError("Pentomino not found on grid")
            current_grid[ny][nx] = '.'


    def contiguous(self, r, c, cnt=5):
        '''
        Must find at least 5 contiguous blocks from the starting position.
        :param cnt:
        :return:
        '''


    def find_contiguous_spaces(self, grid):
        """
        Identifies contiguous groups of empty spaces in a grid using BFS.

        :param grid: 2D list representing the grid.
        :return: List of contiguous groups where each group is a list of (row, col) tuples.
        """
        # Dimensions of the grid
        rows, cols = len(grid), len(grid[0])

        # Directions for adjacency: up, down, left, right
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        def bfs(start_r, start_c):
            """
            Perform BFS to find all contiguous empty cells for a given starting cell.

            :param start_r: Starting row
            :param start_c: Starting column
            :return: List of all (row, col) cells in the current contiguous group.
            """
            # Queue for BFS and list to store the current group
            queue = deque([(start_r, start_c)])
            group = []

            # Mark the starting cell as visited
            visited[start_r][start_c] = True

            while queue:
                r, c = queue.popleft()  # Process the current cell
                group.append((r, c))

                # Check all adjacent cells
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    # Visit valid neighbors that are not visited and are empty
                    if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] == '.':
                        visited[nr][nc] = True  # Mark as visited
                        queue.append((nr, nc))  # Add to the queue for processing

            return group

        # Initialize the visited 2D list locally for this function call
        visited = [[False for _ in range(cols)] for _ in range(rows)]

        # List to store all contiguous groups
        contiguous_groups = []

        # Loop through the entire grid
        for r in range(rows):
            for c in range(cols):
                # If an empty cell hasn't been visited, start a new BFS
                if grid[r][c] == '.' and not visited[r][c]:
                    contiguous_groups.append(bfs(r, c))

        return contiguous_groups

    def is_valid_grid(self, current_grid):
        for space in self.find_contiguous_spaces(current_grid):
            if len(space) % 5 != 0:
                return False
            if len(space) == 5:
                # We can now check if the space matches that of a already included
                # pentomino, then we also have a state where the solution is not valid.
                pass
        return True

    def is_complete(self, current_grid):
        for r in range(len(current_grid)):
            for c in range(len(current_grid[r])):
                if current_grid[r][c] == '.':
                    return False
        return True


    def solve_iterative(self):
        """
        Iterative solver to avoid recursion for DFS using an explicit memory structure.
        :return: True if a solution is found, False otherwise.
        """
        import threading
        from multiprocessing import cpu_count
        
        stack = []  # Threadsafe stack to store state
        stack_lock = threading.Lock()  # Lock for synchronizing stack access
        solution_found_event = threading.Event()  # Event to signal solution found
        num_threads = max(cpu_count() - 2, 1)  # Use all cores except 2
        
        stack.append((self.pentomino_letters, deepcopy(self.grid), 0, 0, 0))
        
        # Sort the stack by the length of remaining pentominoes
        stack.sort(key=lambda state: len(state[0]))
        self.total_solutions_evaluated = 0  # Initialize solution evaluation counter
        
        def worker():
            nonlocal stack
            while not solution_found_event.is_set():
                with stack_lock:
                    if not stack:
                        break  # Exit if stack is empty and no solution found yet
                    # Sort the stack by shortest remaining pentominoes before popping
                    remaining_pentominoes, current_grid, x, y, shape_index = stack.pop()

                self.grid = deepcopy(current_grid)
        
                if not remaining_pentominoes:
                    # Solution found
                    if current_grid not in self.solutions:
                        self.solutions.append(current_grid)
                    if self.is_valid_grid(current_grid) and self.is_complete(current_grid):
                        solution_found_event.set()  # Signal other threads
                        return
        
                # Take first pentomino and attempt placement
                letter = remaining_pentominoes[0]
                shapes = self.pentomino_shapes_dict[letter]
                while shape_index < len(shapes):
                    shape = shapes[shape_index]
                    x = y = 0
        
                    while y < self.grid_height:
                        while x < self.grid_width:
                            if self.is_valid_placement(shape, x, y, current_grid):
                                for dx, dy in shape:
                                    nx, ny = x + dx, y + dy
                                    current_grid[ny][nx] = letter
        
                                next_pentominoes = remaining_pentominoes[1:]
                                if self.is_valid_grid(current_grid):
                                    with stack_lock:
                                        if self.is_complete(current_grid):
                                            self.grid = current_grid
                                            self.solutions.append(current_grid)
                                            solution_found_event.set()  # Signal other threads
                                            return
                                        self.total_solutions_evaluated += 1  # Increment the counter
                                        if self.total_solutions_evaluated % 1000 == 0:
                                            print(f"{self.total_solutions_evaluated} solutions evaluated so far.")

                                        stack.insert(0, (next_pentominoes, deepcopy(current_grid), 0, 0, 0))
                                        self.last_attempt = deepcopy(current_grid)

                                for dx, dy in shape:
                                    nx, ny = x + dx, y + dy
                                    current_grid[ny][nx] = '.'
                            x += 1
                        x = 0
                        y += 1
                    shape_index += 1
        
        threads = [threading.Thread(target=worker) for _ in range(num_threads)]
        
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        return solution_found_event.is_set()  # Return whether a solution was found

    def solve(self):
        result = self.solve_iterative()
        if result:
            print("Solution found:")
            for solution in self.solutions:
                self.print_grid(solution)
        else:
            print("No solution found.")
            self.print_grid()
        return result



if __name__ == '__main__':
    api = PentominoSolverAPI()
    api.run()