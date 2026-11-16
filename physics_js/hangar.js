// Ключ для LocalStorage (пункт 4 ТЗ)
const STORAGE_KEY = 'space_hangar_ships';
let ships = [];
let editingId = null;

// DOM элементы
const form = document.getElementById('ship-form');
const formTitle = document.getElementById('form-title');
const submitBtn = document.getElementById('submit-btn');
const cancelBtn = document.getElementById('cancel-btn');
const container = document.getElementById('ships-container');
const searchInput = document.getElementById('search-input');

// Поля формы
const inputId = document.getElementById('ship-id');
const inputName = document.getElementById('ship-name');
const inputMass = document.getElementById('ship-mass');
const inputThrust = document.getElementById('ship-thrust');
const inputDurability = document.getElementById('ship-durability');

// --- 1. Чтение из LocalStorage (Read - инициализация) ---
function loadShips() {
    const data = localStorage.getItem(STORAGE_KEY);
    ships = data ? JSON.parse(data) : [];
}

// --- 2. Сохранение в LocalStorage (Пункт 4) ---
function saveShips() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(ships));
}

// --- 3. Отрисовка карточек (Read - UI) ---
function renderShips(filterText = '') {
    container.innerHTML = '';
    
    // Пункт 3: Фильтрация и поиск
    const filtered = ships.filter(s => 
        s.name.toLowerCase().includes(filterText.toLowerCase())
    );

    if (filtered.length === 0) {
        container.innerHTML = '<p style="color:#888;">Корабли не найдены.</p>';
        return;
    }

    filtered.forEach(ship => {
        const card = document.createElement('div');
        card.className = 'ship-card';
        card.innerHTML = `
            <h3>${ship.name}</h3>
            <p>Масса: ${ship.mass} т</p>
            <p>Тяга: ${ship.thrust} кН</p>
            <p>Прочность: ${ship.durability}%</p>
            <div class="actions">
                <button class="btn-edit" onclick="editShip(${ship.id})">✏️ Изменить</button>
                <button class="btn-delete" onclick="deleteShip(${ship.id})">🗑️ Удалить</button>
            </div>
        `;
        container.appendChild(card);
    });
}

// --- 4. Создание / Обновление (Create / Update) ---
form.addEventListener('submit', (e) => {
    e.preventDefault(); // Останавливаем перезагрузку страницы

    // Пункт 2: Валидация (HTML5 required + min/max работает через form.checkValidity)
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const shipData = {
        id: editingId || Date.now(), // Используем время как уникальный ID
        name: inputName.value.trim(),
        mass: Number(inputMass.value),
        thrust: Number(inputThrust.value),
        durability: Number(inputDurability.value)
    };

    if (editingId) {
        // UPDATE: Находим индекс и заменяем
        const index = ships.findIndex(s => s.id === editingId);
        if (index !== -1) ships[index] = shipData;
    } else {
        // CREATE: Добавляем нового
        ships.push(shipData);
    }

    saveShips(); // Мгновенная персистентность
    resetForm();
    renderShips(searchInput.value);
});

// --- 5. Удаление (Delete) ---
window.deleteShip = (id) => {
    if (confirm('Вы уверены, что хотите удалить этот корабль?')) {
        ships = ships.filter(s => s.id !== id);
        saveShips();
        renderShips(searchInput.value);
    }
};

// --- 6. Подготовка к редактированию (Update - UI) ---
window.editShip = (id) => {
    const ship = ships.find(s => s.id === id);
    if (!ship) return;

    editingId = id;
    inputId.value = ship.id;
    inputName.value = ship.name;
    inputMass.value = ship.mass;
    inputThrust.value = ship.thrust;
    inputDurability.value = ship.durability;

    formTitle.textContent = 'Редактировать корабль';
    submitBtn.textContent = 'Сохранить изменения';
    cancelBtn.style.display = 'block';
};

// --- Сброс формы ---
function resetForm() {
    form.reset();
    editingId = null;
    inputId.value = '';
    formTitle.textContent = 'Добавить новый корабль';
    submitBtn.textContent = 'Создать корабль';
    cancelBtn.style.display = 'none';
}

cancelBtn.addEventListener('click', resetForm);

// --- Пункт 3: Поиск ---
searchInput.addEventListener('input', (e) => {
    renderShips(e.target.value);
});

// --- Инициализация при загрузке ---
loadShips();
renderShips();