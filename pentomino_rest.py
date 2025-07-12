import threading
import uuid

from flask import Flask, request, jsonify, send_file
import datetime

from pentomino import PentominoSolver
from pentominoDateSolver import PentominoDateSolver

from logging import Logger

LOG = Logger(__name__)

class PentominoSolverAPI:
    def __init__(self):
        self.app = Flask(__name__)
        self.sessions = {}

        @self.app.route('/', methods=['GET'])
        @self.app.route('/index.html', methods=['GET'])
        def serve_index():
            return send_file('index.html')

        @self.app.route('/fav.ico', methods=['GET'])
        def serve_fav_icon():
            return send_file('fav.ico')

        @self.app.route('/gridsolver.html', methods=['GET'])
        def serve_gridsolver():
            return send_file('gridsolver.html')

        @self.app.route('/datesolver.html', methods=['GET'])
        def serve_datesolver():
            return send_file('datesolver.html')

        @self.app.route('/sessions/gridsolver', methods=['POST'])
        def create_session_gridsolver():
            try:
                data = request.json
                session_id = str(uuid.uuid4())
                grid = data['grid']
                grid_width = len(grid[0])
                grid_height = len(grid)
                pentomino_letters = data['selectedPentominoes']
                exclusions = [(ex.get('row'), ex.get('col')) for ex in data.get('exclusions', [])]

                solver = PentominoSolver(grid_width, grid_height, pentomino_letters, exclusions, grid)
                # Remove sessions that have not been accessed in the last 1 hour
                current_time = datetime.datetime.now()
                expired_sessions = [
                    s_id for s_id, s_data in self.sessions.items()
                    if (current_time - s_data['last_access_time']).total_seconds() > 3600
                ]
                for expired_session in expired_sessions:
                    del self.sessions[expired_session]
                
                self.sessions[session_id] = {
                    'solver': solver,
                    'solving_thread': None,
                    'last_access_time': datetime.datetime.now()
                }
                return jsonify({'session_id': session_id}), 201
            except Exception as e:
                return jsonify({'error': str(e)}), 400

        @self.app.route('/sessions/datesolver', methods=['POST'])
        def create_session_datesolver():
            LOG.debug("Creating datesolver session")
            try:
                data = request.json
                session_id = str(uuid.uuid4())
                month = data['month']
                day = int(data['day'])
                dow = data['dow']
                grid = data['grid']

                solver = PentominoDateSolver(month, day, dow, grid)
                # Remove sessions that have not been accessed in the last 1 hour
                current_time = datetime.datetime.now()
                expired_sessions = [
                    s_id for s_id, s_data in self.sessions.items()
                    if (current_time - s_data['last_access_time']).total_seconds() > 3600
                ]
                for expired_session in expired_sessions:
                    del self.sessions[expired_session]

                self.sessions[session_id] = {
                    'solver': solver,
                    'solving_thread': None,
                    'last_access_time': datetime.datetime.now()
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

            solution = None
            if solver.solutions:
                solution = solver.solutions[-1]
            else:
                solution = solver.last_attempt

            response = {
                'total_solutions_evaluated': solver.total_solutions_evaluated,
                'solved': bool(solver.solutions),
                'grid': solution
            }
            return jsonify(response), 200

        @self.app.route('/sessions/<session_id>', methods=['DELETE'])
        def delete_session(session_id):
            if session_id in self.sessions:
                del self.sessions[session_id]
                return jsonify({'message': 'Session deleted'}), 200
            return jsonify({'error': 'Session not found'}), 404

    def run(self, host='0.0.0.0', port=5000):
        self.app.run(host=host, port=port)

if __name__ == "__main__":
    api = PentominoSolverAPI()
    api.run(host='0.0.0.0', port=5000)
