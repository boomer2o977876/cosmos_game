// physics_js/physics.js
import readline from 'readline';

const SCREEN_WIDTH = 900;
const SCREEN_HEIGHT = 800;
const SHIP_RADIUS = 15;
const THRUST = 0.2;
const BRAKE_THRUST = 0.12;

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    terminal: false
});

rl.on('line', (line) => {
    try {
        const data = JSON.parse(line);
        const { ship, asteroids, keys, dt } = data;

        // 1. Физика корабля (Тригонометрия и векторы)
        if (keys.w) {
            ship.vx += THRUST * Math.cos(ship.alpha);
            ship.vy += THRUST * Math.sin(ship.alpha);
        }
        if (keys.s) {
            const speed = Math.hypot(ship.vx, ship.vy);
            if (speed > 0.1) {
                ship.vx -= BRAKE_THRUST * (ship.vx / speed);
                ship.vy -= BRAKE_THRUST * (ship.vy / speed);
            } else {
                ship.vx = 0;
                ship.vy = 0;
            }
        }

        // Обновление позиции корабля и циклический экран
        ship.x += ship.vx * (dt * 60); // умножаем на dt для независимости от FPS
        ship.y += ship.vy * (dt * 60);
        ship.x = ((ship.x % SCREEN_WIDTH) + SCREEN_WIDTH) % SCREEN_WIDTH;
        ship.y = ((ship.y % SCREEN_HEIGHT) + SCREEN_HEIGHT) % SCREEN_HEIGHT;

        // 2. Физика астероидов и проверка коллизий
        let isCollision = false;
        for (let ast of asteroids) {
            ast.x += ast.vx * (dt * 60);
            ast.y += ast.vy * (dt * 60);
            
            // Циклический экран для астероидов
            ast.x = ((ast.x % SCREEN_WIDTH) + SCREEN_WIDTH) % SCREEN_WIDTH;
            ast.y = ((ast.y % SCREEN_HEIGHT) + SCREEN_HEIGHT) % SCREEN_HEIGHT;

            // Проверка коллизий (Теорема Пифагора)
            const dx = ship.x - ast.x;
            const dy = ship.y - ast.y;
            const distance = Math.hypot(dx, dy);
            if (distance < (SHIP_RADIUS + ast.radius)) {
                isCollision = true;
            }
        }

        // Возвращаем результат обратно в Python
        const result = { ship, asteroids, isCollision };
        console.log(JSON.stringify(result));

    } catch (e) {
        console.error("Ошибка парсинга JSON в JS:", e.message);
    }
});