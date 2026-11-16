// web_physics.js
export const SETTINGS = {
    SCREEN_WIDTH: 900,
    SCREEN_HEIGHT: 800,
    SHIP_RADIUS: 15,
    THRUST: 0.2,
    BRAKE_THRUST: 0.12,
    ROTATION_SPEED: 0.05
};

export function updatePhysics(ship, asteroids, keys, dt) {
    // Поворот
    if (keys.a) ship.alpha -= SETTINGS.ROTATION_SPEED;
    if (keys.d) ship.alpha += SETTINGS.ROTATION_SPEED;

    // Тяга (ТУТ ВАЖНЫЙ МОМЕНТ: используем ship.thrustValue, если он есть)
    if (keys.w) {
        const thrust = ship.thrustValue !== undefined ? ship.thrustValue : SETTINGS.THRUST;
        ship.vx += thrust * Math.cos(ship.alpha);
        ship.vy += thrust * Math.sin(ship.alpha);
    }

    // Торможение
    if (keys.s) {
        const speed = Math.hypot(ship.vx, ship.vy);
        if (speed > 0.1) {
            ship.vx -= SETTINGS.BRAKE_THRUST * (ship.vx / speed);
            ship.vy -= SETTINGS.BRAKE_THRUST * (ship.vy / speed);
        } else {
            ship.vx = 0;
            ship.vy = 0;
        }
    }

    // Позиция и wrap-around
    ship.x += ship.vx * (dt * 60);
    ship.y += ship.vy * (dt * 60);
    ship.x = ((ship.x % SETTINGS.SCREEN_WIDTH) + SETTINGS.SCREEN_WIDTH) % SETTINGS.SCREEN_WIDTH;
    ship.y = ((ship.y % SETTINGS.SCREEN_HEIGHT) + SETTINGS.SCREEN_HEIGHT) % SETTINGS.SCREEN_HEIGHT;

    // Астероиды и коллизии
    let isCollision = false;
    for (let ast of asteroids) {
        ast.x += ast.vx * (dt * 60);
        ast.y += ast.vy * (dt * 60);
        ast.x = ((ast.x % SETTINGS.SCREEN_WIDTH) + SETTINGS.SCREEN_WIDTH) % SETTINGS.SCREEN_WIDTH;
        ast.y = ((ast.y % SETTINGS.SCREEN_HEIGHT) + SETTINGS.SCREEN_HEIGHT) % SETTINGS.SCREEN_HEIGHT;

        const dx = ship.x - ast.x;
        const dy = ship.y - ast.y;
        const distance = Math.hypot(dx, dy);
        
        // Если дистанция меньше суммы радиусов
        if (distance < (SETTINGS.SHIP_RADIUS + ast.radius)) {
            isCollision = true;
        }
    }

    return { ship, asteroids, isCollision };
}