from datetime import time

import pytest
from pentominoDateSolver import PentominoDateSolver
import time

def test_pentomino_date_solver_initialization_valid():
    solver = PentominoDateSolver(mon="Mar", day=1, dow="SAT")
    assert solver.width == 9
    assert solver.height == 6
    assert solver.mon == "MAR"
    assert solver.day == "1"
    assert solver.dow == "SAT"
    assert len(solver.exclusions) == 4
    start = time.time()
    solution = solver.solve()
    end = time.time()
    print(f"Solution found in {end - start:.2f} seconds.")
    assert solution is not None

def test_today():
    import datetime
    DOW = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    MONTH = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    today = datetime.date.today()
    day = today.day
    month = MONTH[ today.month - 1 ]
    dow = DOW[today.weekday()]
    solver = PentominoDateSolver(mon=month, day=day, dow=dow)
    solution = solver.solve()





def test_pentomino_date_solver_invalid_month():
    with pytest.raises(ValueError, match="Invalid month"):
        PentominoDateSolver(mon="ABC", day=15, dow="MON")


def test_pentomino_date_solver_invalid_day_low():
    with pytest.raises(ValueError, match="Value error invalid day"):
        PentominoDateSolver(mon="JAN", day=0, dow="MON")


def test_pentomino_date_solver_invalid_day_high():
    with pytest.raises(ValueError, match="Value error invalid day"):
        PentominoDateSolver(mon="JAN", day=32, dow="MON")


def test_pentomino_date_solver_invalid_dow():
    with pytest.raises(ValueError, match="Value error invalid day"):
        PentominoDateSolver(mon="JAN", day=15, dow="XYZ")
