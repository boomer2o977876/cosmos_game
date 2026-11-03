// physics_js/selftest.js
import { strict as assert } from 'assert';

let passed = 0;
let failed = 0;

function test(description, fn) {
    try {
        fn();
        passed++;
        console.log(`✅ ${description}`);
    } catch (e) {
        failed++;
        console.error(`❌ ОШИБКА: ${description}`);
        console.error(`   ${e.message}`);
    }
}

// Константы (синхронизированы с physics.js и settings.py)
const SCREEN_WIDTH = 900;
const SCREEN_HEIGHT = 800;
const SHIP_RADIUS = 15;
const THRUST = 0.2;
const BRAKE_THRUST = 0.12;

console.log("--- Запуск самопроверки физики на JavaScript ---\n");

// ==========================================
// 1. ТЕСТЫ ТРИГОНОМЕТРИИ И ВЕКТОРОВ
// ==========================================
test("Тяга под углом 0 градусов (вправо) добавляет скорость по X", () => {
    let vx = 0, vy = 0, alpha = 0;
    vx += THRUST * Math.cos(alpha);
    vy += THRUST * Math.sin(alpha);
    assert.ok(vx > 0.19 && vx < 0.21, "Скорость по X должна быть ~0.2");
    assert.ok(Math.abs(vy) < 0.001, "Скорость по Y должна быть 0");
});

test("Тяга под углом 90 градусов (вниз) добавляет скорость по Y", () => {
    let vx = 0, vy = 0, alpha = Math.PI / 2;
    vx += THRUST * Math.cos(alpha);
    vy += THRUST * Math.sin(alpha);
    assert.ok(Math.abs(vx) < 0.001, "Скорость по X должна быть 0");
    assert.ok(vy > 0.19 && vy < 0.21, "Скорость по Y должна быть ~0.2");
});

test("Тяга под углом 45 градусов распределяет скорость", () => {
    let vx = 0, vy = 0, alpha = Math.PI / 4;
    vx += THRUST * Math.cos(alpha);
    vy += THRUST * Math.sin(alpha);
    assert.ok(Math.abs(vx - vy) < 0.001, "Скорости по X и Y должны быть равны");
});

// ==========================================
// 2. ТЕСТЫ ТОРМОЖЕНИЯ (Пороговые условия)
// ==========================================
test("Торможение уменьшает длину вектора скорости", () => {
    let vx = 5, vy = 0;
    const speed = Math.hypot(vx, vy);
    vx -= BRAKE_THRUST * (vx / speed);
    assert.ok(vx < 5, "Скорость должна уменьшиться");
});

test("Торможение обнуляет скорость ниже порога 0.1", () => {
    let vx = 0.05, vy = 0.05;
    const speed = Math.hypot(vx, vy);
    if (speed > 0.1) {
        vx -= BRAKE_THRUST * (vx / speed);
    } else {
        vx = 0; vy = 0;
    }
    assert.equal(vx, 0, "Скорость по X должна стать строго 0");
    assert.equal(vy, 0, "Скорость по Y должна стать строго 0");
});

// ==========================================
// 3. ТЕСТЫ ЦИКЛИЧЕСКОГО ЭКРАНА (Wrap-around)
// ==========================================
test("Телепортация с левого края на правый", () => {
    let x = -10;
    x = ((x % SCREEN_WIDTH) + SCREEN_WIDTH) % SCREEN_WIDTH;
    assert.equal(x, 890, "Корабль должен появиться справа (900 - 10)");
});

test("Телепортация с правого края на левый", () => {
    let x = SCREEN_WIDTH + 20;
    x = ((x % SCREEN_WIDTH) + SCREEN_WIDTH) % SCREEN_WIDTH;
    assert.equal(x, 20, "Корабль должен появиться слева");
});

test("Телепортация с верхнего края на нижний", () => {
    let y = -15;
    y = ((y % SCREEN_HEIGHT) + SCREEN_HEIGHT) % SCREEN_HEIGHT;
    assert.equal(y, SCREEN_HEIGHT - 15, "Астероид должен появиться внизу");
});

test("Телепортация с нижнего края на верхний", () => {
    let y = SCREEN_HEIGHT + 5;
    y = ((y % SCREEN_HEIGHT) + SCREEN_HEIGHT) % SCREEN_HEIGHT;
    assert.equal(y, 5, "Астероид должен появиться наверху");
});

// ==========================================
// 4. ТЕСТЫ КОЛЛИЗИЙ (Теорема Пифагора)
// ==========================================
test("Коллизия: объекты пересекаются", () => {
    const ship = { x: 100, y: 100 };
    const ast = { x: 110, y: 110, radius: 20 };
    const distance = Math.hypot(ship.x - ast.x, ship.y - ast.y);
    const isColliding = distance < (SHIP_RADIUS + ast.radius);
    assert.equal(isColliding, true, "Должна быть коллизия (расстояние < суммы радиусов)");
});

test("Коллизия: объекты на грани касания", () => {
    const ship = { x: 100, y: 100 };
    const ast = { x: 135, y: 100, radius: 20 }; // 15 (корабль) + 20 (астероид) = 35
    const distance = Math.hypot(ship.x - ast.x, ship.y - ast.y);
    const isColliding = distance < (SHIP_RADIUS + ast.radius);
    assert.equal(isColliding, false, "При точном касании коллизии нет (строгое неравенство)");
});

test("Коллизия: объекты далеко друг от друга", () => {
    const ship = { x: 100, y: 100 };
    const ast = { x: 500, y: 500, radius: 20 };
    const distance = Math.hypot(ship.x - ast.x, ship.y - ast.y);
    const isColliding = distance < (SHIP_RADIUS + ast.radius);
    assert.equal(isColliding, false, "Коллизии быть не должно");
});

// ==========================================
// 5. ТЕСТЫ ДВИЖЕНИЯ
// ==========================================
test("Движение корабля по инерции", () => {
    const dt = 0.016; // ~60 FPS
    let x = 100, y = 100, vx = 2, vy = -3;
    x += vx * (dt * 60);
    y += vy * (dt * 60);
    assert.ok(x > 100, "Корабль сдвинулся вправо");
    assert.ok(y < 100, "Корабль сдвинулся вверх");
});

test("Скорость света (проверка Math.hypot)", () => {
    const speed = Math.hypot(3, 4);
    assert.equal(speed, 5, "3-4-5 прямоугольный треугольник");
});

// ==========================================
// 6. ВАЛИДАЦИЯ (Имитация LevelManager)
// ==========================================
test("Валидация JSON: успешный парсинг", () => {
    const data = '{"width": 800, "height": 600}';
    const parsed = JSON.parse(data);
    assert.equal(parsed.width, 800);
    assert.equal(parsed.height, 600);
});

test("Валидация JSON: обработка ошибки", () => {
    const data = '{"width": 800, "height": }'; // Битый JSON
    let caught = false;
    try {
        JSON.parse(data);
    } catch (e) {
        caught = true;
    }
    assert.equal(caught, true, "Битый JSON должен выбрасывать исключение");
});

test("Валидация обязательных полей", () => {
    const data = { width: 800 }; // Нет height
    const required = ["width", "height"];
    let missing = false;
    for (const field of required) {
        if (data[field] === undefined) missing = true;
    }
    assert.equal(missing, true, "Система должна обнаружить отсутствие поля height");
});

// ==========================================
// 7. ТЕСТЫ СЛОЖНЫХ МАТЕМАТИЧЕСКИХ ОПЕРАЦИЙ
// ==========================================
test("Нормализация вектора (деление на длину)", () => {
    let vx = 10, vy = 0;
    const speed = Math.hypot(vx, vy);
    const nx = vx / speed;
    const ny = vy / speed;
    assert.equal(nx, 1);
    assert.equal(ny, 0);
});

test("Обработка отрицательных чисел в остатке от деления (%)", () => {
    const val = -5 % 900;
    assert.equal(val, -5, "В JS остаток от отрицательного числа отрицательный");
    const fixed = ((val % 900) + 900) % 900;
    assert.equal(fixed, 895, "Формула wrap-around должна превратить -5 в 895");
});

test("Модуль числа через Math.abs", () => {
    assert.equal(Math.abs(-15), 15);
});

test("Сравнение с плавающей точкой (Эпсилон)", () => {
    const a = 0.1 + 0.2;
    // В JS 0.1 + 0.2 !== 0.3
    assert.ok(Math.abs(a - 0.3) < 1e-10, "Плавающая точка сравнена с погрешностью");
});

console.log(`\n=========================================`);
console.log(`РЕЗУЛЬТАТ: ${passed} пройдено, ${failed} провалено.`);
console.log(`=========================================`);

if (failed > 0) {
    process.exit(1);
}