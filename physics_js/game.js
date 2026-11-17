import { updatePhysics, SETTINGS } from './web_physics.js';

// --- DOM Элементы ---
const screens = {
    menu: document.getElementById('menu-screen'),
    game: document.getElementById('game-screen'),
    scores: document.getElementById('scores-screen'),
    hangar: document.getElementById('hangar-screen')
};
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const btnStart = document.getElementById('btn-start');
const shipSelector = document.getElementById('ship-selector');
const scoresBody = document.getElementById('scores-body');
const pauseOverlay = document.getElementById('pause-overlay');

const hpBar = document.getElementById('hp-bar');
const hpText = document.getElementById('hp-text');
const scoreText = document.getElementById('score-text');
const speedText = document.getElementById('speed-text');
const sidebarShipSelector = document.getElementById('sidebar-ship-selector');

document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        // Снимаем активный класс со всех кнопок
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');

        // Показываем нужный экран
        const target = e.target.dataset.target;
        Object.values(screens).forEach(s => s.classList.remove('active'));
        screens[target.replace('-screen', '')].classList.add('active');

        // Скрываем выбор корабля, если мы не в меню
        sidebarShipSelector.style.display = (target === 'menu-screen') ? 'block' : 'none';
        
        // ВАЖНО: Обновляем списки при переключении вкладок!
        if (target === 'menu-screen') {
            loadShips(); // Перечитываем localStorage и обновляем select
        }
        if (target === 'scores-screen') {
            renderScores();
        }
    });
});

// --- Состояние игры ---
let ship = { x: 450, y: 400, vx: 0, vy: 0, alpha: 0, thrustValue: 0.2 };
let asteroids = [];
let particles = [];
let isGodMode = false;
let isHyperdrive = false;
let isPaused = false;
let isPlaying = false;
let animationId = null;

let isInvulnerable = false;
let invulnerableTimer = 0;

let score = 0;
let startTime = 0;
let currentDurability = 100;
let maxDurability = 100;
let activeShipName = "Стандартный";

// Флаги клавиатуры
const keys = { w: false, a: false, s: false, d: false };

// --- СЛУШАТЕЛИ КЛАВИАТУРЫ ---
// --- СЛУШАТЕЛИ КЛАВИАТУРЫ (Независимо от раскладки) ---
window.addEventListener('keydown', (e) => {
    // e.code возвращает физический код клавиши (KeyW, KeyA, KeyS, KeyD, Escape)
    
    if (e.code === 'KeyW') keys.w = true;
    if (e.code === 'KeyA') keys.a = true;
    if (e.code === 'KeyS') keys.s = true;
    if (e.code === 'KeyD') keys.d = true;

    // Пауза по Escape
    if (e.code === 'Escape' && isPlaying) {
        isPaused = !isPaused;
        pauseOverlay.style.display = isPaused ? 'flex' : 'none';
        if (!isPaused) {
            lastTime = performance.now(); 
            requestAnimationFrame(gameLoop);
        }
    }
});

window.addEventListener('keyup', (e) => {
    if (e.code === 'KeyW') keys.w = false;
    if (e.code === 'KeyA') keys.a = false;
    if (e.code === 'KeyS') keys.s = false;
    if (e.code === 'KeyD') keys.d = false;
});

window.addEventListener('keyup', (e) => {
    const k = e.key.toLowerCase();
    if (k in keys) {
        keys[k] = false;
        console.log(`[KEYUP] ${k} = false`); // Отладка
    }
});

function showScreen(name) {
    Object.values(screens).forEach(s => s.classList.remove('active'));
    screens[name].classList.add('active');
}

function loadShips() {
    const savedShips = JSON.parse(localStorage.getItem('space_hangar_ships') || '[]');
    shipSelector.innerHTML = '<option value="">Стандартный корабль</option>';
    savedShips.forEach(s => {
        const opt = document.createElement('option');
        opt.value = s.id;
        opt.textContent = s.name;
        shipSelector.appendChild(opt);
    });
}

function applyShipStats() {
    const activeId = shipSelector.value;
    const savedShips = JSON.parse(localStorage.getItem('space_hangar_ships') || '[]');
    const activeShip = savedShips.find(s => s.id == activeId);

   if (activeShip) {
        // Ограничиваем базовую тягу, чтобы корабль не улетал за край экрана за 1 кадр
        ship.thrustValue = Math.min(0.4, 0.2 * (activeShip.thrust / 500)); 
        maxDurability = activeShip.durability;
        activeShipName = activeShip.name;
        ship.color = '#4af';
    } else {
        ship.thrustValue = 0.2;
        maxDurability = 100;
        activeShipName = "Стандартный";
        ship.color = '#fff';
    }
    currentDurability = maxDurability;
}

function startGame() {
    ship = { x: 450, y: 400, vx: 0, vy: 0, alpha: 0, thrustValue: 0.2 };
    asteroids = [];
    particles = [];
    isPaused = false;
    score = 0;
    isInvulnerable = false;
    invulnerableTimer = 0;
    currentDurability = maxDurability;
    
    applyShipStats();
    startTime = performance.now();
    
    for (let i = 0; i < 3; i++) spawnAsteroid();

    showScreen('game');
    isPlaying = true;

    setTimeout(() => canvas.focus(), 50);

    if (document.activeElement) {
        document.activeElement.blur();
    }

    canvas.focus(); 
    console.log("Игра началась. Ожидание ввода...");

    lastTime = performance.now();
    requestAnimationFrame(gameLoop);
}

function spawnAsteroid() {
    const side = Math.floor(Math.random() * 4);
    let x, y;
    if (side === 0) { x = Math.random() * 900; y = -40; }
    else if (side === 1) { x = Math.random() * 900; y = 840; }
    else if (side === 2) { x = -40; y = Math.random() * 800; }
    else { x = 940; y = Math.random() * 800; }

    asteroids.push({
        x, y,
        vx: (Math.random() - 0.5) * 4,
        vy: (Math.random() - 0.5) * 4,
        radius: Math.floor(15 + Math.random() * 15),
        opacity: 1.0, 
        craters: Array.from({ length: 3 }, () => ({
            dx: (Math.random() - 0.5) * 15,
            dy: (Math.random() - 0.5) * 15,
            r: 2 + Math.random() * 3
        }))
    });
}

function saveScore() {
    const timeAlive = Math.floor((performance.now() - startTime) / 1000);
    const records = JSON.parse(localStorage.getItem('flight_records') || '[]');
    records.push({ time: timeAlive, ship: activeShipName, date: new Date().toLocaleString('ru-RU') });
    records.sort((a, b) => b.time - a.time);
    localStorage.setItem('flight_records', JSON.stringify(records.slice(0, 50)));
}

function renderScores() {
    const records = JSON.parse(localStorage.getItem('flight_records') || '[]');
    scoresBody.innerHTML = '';
    if (records.length === 0) {
        scoresBody.innerHTML = '<tr><td colspan="4" style="text-align:center;">Пока нет полетов</td></tr>';
        return;
    }
    records.forEach((r, index) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${index + 1}</td><td style="color:#0f0;font-weight:bold;">${r.time} сек</td><td>${r.ship}</td><td style="color:#888;">${r.date}</td>`;
        scoresBody.appendChild(tr);
    });
}

function draw() {
    ctx.fillStyle = isHyperdrive ? 'rgba(0, 20, 40, 0.4)' : '#000';
    ctx.fillRect(0, 0, 900, 800);

    asteroids.forEach(ast => {
        ctx.save();
        ctx.globalAlpha = ast.opacity;
        ctx.beginPath();
        ctx.arc(ast.x, ast.y, ast.radius, 0, Math.PI * 2);
        ctx.fillStyle = '#999';
        ctx.fill();
        ctx.strokeStyle = '#666';
        ctx.stroke();
        ctx.fillStyle = '#777';
        ast.craters.forEach(c => {
            ctx.beginPath();
            ctx.arc(ast.x + c.dx, ast.y + c.dy, c.r, 0, Math.PI * 2);
            ctx.fill();
        });
        ctx.restore();
    });

    particles.forEach(p => {
        ctx.fillStyle = p.color;
        ctx.globalAlpha = p.life;
        ctx.beginPath();
        ctx.arc(p.x, p.y, 3, 0, Math.PI * 2);
        ctx.fill();
        ctx.globalAlpha = 1.0;
    });

    // Корабль
    ctx.save();
    ctx.translate(ship.x, ship.y);
    ctx.rotate(ship.alpha);
    
    // Мигание при неуязвимости
    if (isInvulnerable && Math.floor(invulnerableTimer / 100) % 2 === 0) {
        ctx.globalAlpha = 0.3; 
    }

    ctx.beginPath();
    ctx.moveTo(SETTINGS.SHIP_RADIUS, 0);
    ctx.lineTo(-SETTINGS.SHIP_RADIUS * 0.7, -SETTINGS.SHIP_RADIUS * 0.7);
    ctx.lineTo(-SETTINGS.SHIP_RADIUS * 0.7, SETTINGS.SHIP_RADIUS * 0.7);
    ctx.closePath();
    
    // Красим в желтый, если включен God Mode, иначе в цвет из конфига
    ctx.fillStyle = isGodMode ? '#ff0' : (ship.color || '#fff');
    ctx.fill();
    
    // Добавляем обводку (синий неон)
    ctx.strokeStyle = '#4af';
    ctx.lineWidth = 2;
    ctx.stroke();
    
    ctx.restore();
    // --- КОНЕЦ ОТРИСОВКИ КОРАБЛЯ ---

}

function createParticles() {
    if (!keys.w) return;
    const angle = ship.alpha + Math.PI;
    const spread = (Math.random() - 0.5) * 0.5;
    particles.push({
        x: ship.x + Math.cos(angle) * 20,
        y: ship.y + Math.sin(angle) * 20,
        vx: Math.cos(angle + spread) * (2 + Math.random() * 2),
        vy: Math.sin(angle + spread) * (2 + Math.random() * 2),
        life: 1.0,
        color: isHyperdrive ? '#0ff' : '#f80'
    });
}

function updateParticles() {
    for (let i = particles.length - 1; i >= 0; i--) {
        const p = particles[i];
        p.x += p.vx;
        p.y += p.vy;
        p.life -= 0.03;
        if (p.life <= 0) particles.splice(i, 1);
    }
}

function updateHUD(speed) {
    // 1. Обновление здоровья (HP)
    const hpPercent = (currentDurability / maxDurability) * 100;
    hpBar.style.width = `${hpPercent}%`;
    hpText.textContent = `${Math.round(currentDurability)}/${maxDurability}`;

    // Меняем цвет от зеленого к красному
    if (hpPercent > 60) hpBar.style.backgroundColor = '#0f0'; // Зеленый
    else if (hpPercent > 25) hpBar.style.backgroundColor = '#f80'; // Оранжевый
    else hpBar.style.backgroundColor = '#f00'; // Красный

    // 2. Обновление счета
    scoreText.textContent = score;

    // 3. Обновление скорости (Меняем цвет текста, если скорость критическая)
    speedText.textContent = speed.toFixed(2);
    if (speed > 6.0) speedText.style.color = '#f00'; // Перенапряжение двигателя
    else speedText.style.color = '#4af';
}

const TIME_STEP = 1000 / 60;
let accumulator = 0;
let lastTime = performance.now();

function gameLoop(currentTime) {
    if (isPaused || !isPlaying) return;

    let deltaTime = currentTime - lastTime;
    lastTime = currentTime;
    if (deltaTime > 100) deltaTime = 100;

    accumulator += deltaTime;

    while (accumulator >= TIME_STEP) {
        score = Math.floor((performance.now() - startTime) / 1000);
        
        // ОТЛАДКА ФИЗИКИ
        if (keys.w) console.log("Тяга активна. vx до:", ship.vx, "vy до:", ship.vy);

        const result = updatePhysics(ship, asteroids, keys, TIME_STEP / 1000);
        
        if (result.isCollision && !isGodMode && !isInvulnerable) {
            currentDurability -= 15; // Урон
            asteroids.forEach(a => a.opacity = 0.3);
            
            // Отталкивание от астероида
            const dx = ship.x - asteroids[0].x;
            const dy = ship.y - asteroids[0].y;
            const dist = Math.hypot(dx, dy);
            
            if (dist > 0) {
                ship.vx += (dx / dist) * 3;
                ship.vy += (dy / dist) * 3;
            }

            // Ограничиваем максимальную скорость
            const MAX_SPEED = 5.0;
            const currentSpeed = Math.hypot(ship.vx, ship.vy);
            if (currentSpeed > MAX_SPEED) {
                ship.vx = (ship.vx / currentSpeed) * MAX_SPEED;
                ship.vy = (ship.vy / currentSpeed) * MAX_SPEED;
            }

            // Включаем неуязвимость
            isInvulnerable = true;
            invulnerableTimer = 1000; // 1 секунда

            if (currentDurability <= 0) {
                isPlaying = false;
                saveScore();
                showScreen('menu');
                loadShips();
                return; 
            }
        }

        // ТАЙМЕР НЕУЯЗВИМОСТИ (Вычитаем время кадра)
        if (isInvulnerable) {
            invulnerableTimer -= TIME_STEP; // Уменьшаем на 16.6 мс каждый шаг физики
            if (invulnerableTimer <= 0) {
                isInvulnerable = false; // Выключаем, когда время вышло
            }
        }
        

        

        asteroids.forEach(a => {
            if (a.opacity < 1.0) a.opacity += 0.05;
        });

        createParticles();
        updateParticles();
        accumulator -= TIME_STEP;
    }

    draw();

    const currentSpeed = Math.hypot(ship.vx, ship.vy);
    updateHUD(currentSpeed);

    animationId = requestAnimationFrame(gameLoop);
}

// Обработчик старта игры (кнопка в главном меню)
btnStart.addEventListener('click', startGame);

// Загружаем корабли при старте
loadShips();


sidebarShipSelector.style.display = 'block';