# File: tests/test_pentomino.py

import pytest
from pentomino import PentominoSolver


def test_pentomino_solver_initialization():
    solver = PentominoSolver(grid_width=10, grid_height=6, pentomino_letters=["P", "X"], exclusions=[])
    assert solver.grid_width == 10
    assert solver.grid_height == 6
    assert solver.pentomino_letters == ["P", "X"]

    with pytest.raises(ValueError):
        PentominoSolver(grid_width=0, grid_height=6, pentomino_letters=["P", "X"], exclusions=[])
    with pytest.raises(ValueError):
        PentominoSolver(grid_width=10, grid_height=-5, pentomino_letters=["P", "X"], exclusions=[])


def test_pentomino_shapes():
    solver = PentominoSolver(grid_width=10, grid_height=6, pentomino_letters=["P", "X"], exclusions=[])
    shapes = solver.pentomino_shapes()
    assert isinstance(shapes, dict)
    assert "P" in shapes
    assert "X" in shapes

    with pytest.raises(ValueError):
        PentominoSolver(grid_width=10, grid_height=6, pentomino_letters=["P", "INVALID"], exclusions=[]).pentomino_shapes()


def test_is_valid_placement():
    solver = PentominoSolver(grid_width=10, grid_height=6, pentomino_letters=["P", "X"], exclusions=[])
    shape = [[1, 1], [1, 0]]
    assert solver.is_valid_placement(shape, 0, 0)
    assert not solver.is_valid_placement(shape, 10, 10)


def test_place_pentomino():
    solver = PentominoSolver(grid_width=10, grid_height=6, pentomino_letters=["P", "X"], exclusions=[])
    shape = [[1, 1], [1, 0]]
    solver.place_pentomino(shape, 0, 0, "P")
    assert solver.grid[0][0] == "P"
    assert solver.grid[1][0] == "P"
    assert solver.grid[0][1] == "P"

    with pytest.raises(IndexError):
        solver.place_pentomino(shape, 9, 5, "P")  # Out of bounds


def test_remove_pentomino():
    solver = PentominoSolver(grid_width=10, grid_height=6, pentomino_letters=["P", "X"], exclusions=[])
    pShapes = solver.get_shapes("I")
    for shape in pShapes:
        solver.place_pentomino(shape, 0, 0, "I")
        solver.remove_pentomino(shape, 0, 0)

    assert solver.grid[0][0] == "."
    assert solver.grid[1][0] == "."
    assert solver.grid[0][1] == "."

    with pytest.raises(ValueError):
        solver.remove_pentomino(shape, 5, 5)  # Attempting to remove pentomino from an empty location


def test_contiguous_spaces():
    solver = PentominoSolver(grid_width=10, grid_height=6, pentomino_letters=["P", "X"], exclusions=[(9,5), (0,2), (0,4), (9,4)])
    assert len(solver.find_contiguous_spaces(solver.grid)) > 0


def test_is_valid_grid():
    solver = PentominoSolver(grid_width=10, grid_height=6, pentomino_letters=["P", "X"], exclusions=[])
    assert solver.is_valid_grid()


def test_dfs():
    solver = PentominoSolver(grid_width=10, grid_height=6, pentomino_letters=["P", "X"], exclusions=[])
    assert solver.dfs(solver.pentomino_letters) is not None

    with pytest.raises(KeyError):
        solver.dfs(["INVALID"])  # Unsupported pentomino letters


import time


def test_solve():
    solver = PentominoSolver(grid_width=3, grid_height=7, pentomino_letters=['V', 'U','Z','P'], exclusions=[(2,1)])
    start_time = time.time()
    solution = solver.solve()
    end_time = time.time()
    print(f"Solution found in {end_time - start_time:.2f} seconds.")
    assert solution is not None


def test_x():
    solver = PentominoSolver(grid_width=3, grid_height=7, pentomino_letters=['V', 'U','Z','P'], exclusions=[(2,1)])
    solution = solver.get_all_shapes('I')


def test_solve():
    solver = PentominoSolver(grid_width=9, grid_height=6, pentomino_letters=['I', 'V','U','Z', 'P', 'Y', 'L', 'F','N', 'T'], exclusions=[(1,1), (4,1), (5,1), (4,2), (5,2), (4,3), (5,3), (4,5), (5,8)])
    start_time = time.time()
    solution = solver.solve()
    end_time = time.time()
    print(f"Solution found in {end_time - start_time:.2f} seconds.")
    assert solution is not None


def test_is_complete():
    grid = [
        ["1", "2", "3",],
        ["4", "5", "6",],
        ["7", "8", "9", ],
        ["x", ".", "x", ],
    ]
    solver = PentominoSolver(grid_width=3, grid_height=4, pentomino_letters=['I', 'V','U','Z', 'P', 'Y', 'L', 'F'], exclusions=[(3,0), (3,2)])
    assert not solver.is_complete(grid)

    grid = [
        ["1", "2", "3",],
        ["4", "5", "6",],
        ["7", "8", "9", ],
        ["x", "0", "x", ],
    ]

    assert solver.is_complete(grid)
    grid = [
        ["x", "x", "x", "x", "x", "x", "P", "P", "P",],
        ["x", "x", "x", "x", "x", "x", "P", "P", "Y"],
        ["V", "V", "V", "I", "I", "I", "I", "I", "Y",],
        ["V", "Z", "Z", "L", "L", "L", "L", "Y", "Y",],
        ["V", "Z", "x", ".", ".", "U", "L", "U", "Y"],
        ["Z", "Z", ".", ".", ".", "U", "U", "U", "x"],
    ]


    solver = PentominoSolver(grid_width=9, grid_height=6, pentomino_letters=['I', 'V', 'U', 'Z', 'P', 'Y', 'L', 'F'],
                             exclusions=[(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (1, 0), (1, 1), (1, 2), (1, 3),
                                         (1, 4), (1, 5), (4, 2), (5, 8)]
    )
    assert solver.is_complete(grid)
