# physics_bridge.py
import subprocess
import json
import os

class JSPhysicsEngine:
    def __init__(self):
        # Путь к скрипту JS
        js_path = os.path.join(os.path.dirname(__file__), "physics_js", "physics.js")
        
        # Запускаем node physics.js
        self.process = subprocess.Popen(
            ["node", js_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

    def update(self, ship, asteroids, keys, dt):
        # Формируем данные для JS
        payload = {
            "ship": {"x": ship.x, "y": ship.y, "vx": ship.vx, "vy": ship.vy, "alpha": ship.alpha},
            "asteroids": [{"x": a.x, "y": a.y, "vx": a.vx, "vy": a.vy, "radius": a.radius} for a in asteroids],
            "keys": keys,
            "dt": dt
        }
        
        # Отправляем в stdin JS
        self.process.stdin.write(json.dumps(payload) + "\n")
        self.process.stdin.flush()
        
        # Читаем ответ из stdout
        line = self.process.stdout.readline()
        if not line:
            return None, None, False
            
        result = json.loads(line)
        
        # Обновляем Python-объекты полученными значениями
        ship.x = result["ship"]["x"]
        ship.y = result["ship"]["y"]
        ship.vx = result["ship"]["vx"]
        ship.vy = result["ship"]["vy"]

        for py_ast, js_ast in zip(asteroids, result["asteroids"]):
            py_ast.x = js_ast["x"]
            py_ast.y = js_ast["y"]

        return ship, asteroids, result["isCollision"]

    def close(self):
        self.process.terminate()