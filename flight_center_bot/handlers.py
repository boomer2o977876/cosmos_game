from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup

from analytics import load_sectors, top_by_distance, flight_summary, player_stats
from keyboards import main_menu_kb, back_kb
from session_store import get_session, set_session, clear_session

router = Router()

class UploadStates(StatesGroup):
    waiting_for_csv = State()

async def _safe_edit(callback: CallbackQuery, text: str, kb: InlineKeyboardMarkup):
    """edit_text с защитой от 'message is not modified'."""
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        pass
    await callback.answer()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await clear_session(message.from_user.id)
    await message.answer(
        "<b>Центр Полётов</b>\nВыбери раздел:",
        reply_markup=main_menu_kb(),
        parse_mode="HTML",
    )

@router.callback_query(F.data == "menu:back")
async def cb_back(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await _safe_edit(callback, "<b>Центр Полётов</b>\nВыбери раздел:", main_menu_kb())

@router.callback_query(F.data == "menu:top")
async def cb_top(callback: CallbackQuery):
    sectors = load_sectors()
    ranking = top_by_distance(sectors, limit=5)
    
    lines = [f"<b>🏆 Топ полётов по дистанции</b>\nСектор: {sectors.get('sector_name', '—')}\n"]
    
    if not ranking:
        lines.append("Нет данных в логе.")
    else:
        for i, rec in enumerate(ranking, start=1):
            lines.append(
                f"{i}. <b>{rec['distance']:.0f} м</b> (Ур. {rec['level']}: {rec['level_name']})\n"
                f"   <i>Время: {rec['time']}</i>"
            )
            
    await _safe_edit(callback, "\n".join(lines), back_kb())

@router.callback_query(F.data == "menu:flight")
async def cb_flight(callback: CallbackQuery):
    s = flight_summary()
    if s['sessions'] == 0:
        text = "<b>✈️ Сводка «Чёрного ящика»</b>\n\nВ логе пока нет данных."
    else:
        text = (
            "<b>✈️ Сводка «Чёрного ящика»</b>\n\n"
            f"Всего сессий: <b>{s['sessions']}</b>\n"
            f"Суммарная дистанция: <b>{s['total_distance']:.0f}</b> м\n"
            f"Макс. скорость: <b>{s['max_speed']:.2f}</b>\n"
            f"Время в логе: <b>{s['total_time']}</b> сек."
        )
    await _safe_edit(callback, text, back_kb())

@router.callback_query(F.data == "menu:stats")
async def cb_stats(callback: CallbackQuery):
    st = player_stats(callback.from_user.id)
    if st['flights'] == 0:
        text = "<b>📊 Статистика пилота</b>\n\nВ логах пока нет ни одного полёта."
    else:
        text = (
            "<b>📊 Статистика сектора</b>\n\n"
            f"Всего полётов: <b>{st['flights']}</b>\n"
            f"Суммарная дистанция: <b>{st['total_distance']:.0f}</b> м\n"
            f"Максимальный уровень: <b>{st['best_level']}</b>"
        )
    await _safe_edit(callback, text, back_kb())

@router.callback_query(F.data == "menu:ach")
async def cb_ach(callback: CallbackQuery):
    st = player_stats(callback.from_user.id)
    ach = st.get("achievements", [])
    
    if not ach:
        text = "<b>🎖 Достижения</b>\n\nПока нет достижений. Летайте больше!"
    else:
        text = "<b>🎖 Достижения сектора</b>\n\n" + "\n".join(f"• {a}" for a in ach)
        
    await _safe_edit(callback, text, back_kb())

@router.callback_query(F.data == "menu:upload")
async def cb_upload(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UploadStates.waiting_for_csv)
    await _safe_edit(
        callback,
        "<b>📤 Загрузка CSV</b>\n\nОтправь файл с расширением <code>.csv</code>.",
        back_kb(),
    )

@router.message(UploadStates.waiting_for_csv, ~F.document)
async def handle_wrong_upload(message: Message):
    """Если пользователь прислал текст или фото вместо файла."""
    await message.answer("⚠️ Пожалуйста, отправьте именно <b>файл</b> с расширением <code>.csv</code>.", parse_mode="HTML")

@router.message(UploadStates.waiting_for_csv, F.document)
async def handle_csv(message: Message, state: FSMContext, bot: Bot):
    doc = message.document
    if not doc.file_name.lower().endswith(".csv"):
        await message.answer("⚠️ Нужен именно формат <code>.csv</code>.", parse_mode="HTML")
        return
        
    try:
        file = await bot.get_file(doc.file_id)
        raw = await bot.download_file(file.file_path)
        # Пытаемся декодировать, если не выйдет - выбросит ошибку, которую мы поймаем
        text = raw.read().decode("utf-8", errors="ignore") 
    except Exception as e:
        await message.answer("❌ Не удалось прочитать файл. Возможно, он поврежден.")
        await state.clear()
        return

    first_line = text.splitlines()[0] if text else ""
    required = {"date", "score", "level"}
    
    # Проверяем, что заголовки на месте
    if not required.issubset({c.strip() for c in first_line.split(",")}):
        await message.answer("❌ CSV не прошёл верификацию: нет колонок <code>date</code>, <code>score</code> или <code>level</code>.", parse_mode="HTML")
        await state.clear()
        return
    # Сохраняем «принят» в сессию (можно расширить парсинг)
    sess = await get_session(message.from_user.id)
    sess["last_upload"] = {"file": doc.file_name, "rows": len(text.splitlines()) - 1}
    await set_session(message.from_user.id, sess)
    await state.clear()
    await message.answer(
        f"✅ Принято: <b>{doc.file_name}</b>\nСтрок: {sess['last_upload']['rows']}",
        reply_markup=main_menu_kb(),
        parse_mode="HTML",
    )

@router.callback_query(F.data == "menu:watch")
async def cb_watch(callback: CallbackQuery):
    sess = await get_session(callback.from_user.id)
    enabled = sess.get("watch", False)
    sess["watch"] = not enabled
    await set_session(callback.from_user.id, sess)
    status = "включены 🔔" if sess["watch"] else "выключены 🔕"
    await _safe_edit(
        callback,
        f"<b>🔔 Уведомления</b>\n\nСейчас: <b>{status}</b>\nНажми ещё раз, чтобы переключить.",
        back_kb(),
    )

# --- Текстовые команды (дублируют кнопки, если пользователь пишет вручную) ---
@router.message(Command("top"))
async def cmd_top(message: Message):
    sectors = load_sectors()
    ranking = top_by_distance(sectors, limit=5)
    lines = [f"<b>🏆 Топ полётов по дистанции</b>\nСектор: {sectors.get('sector_name', '—')}\n"]
    for i, rec in enumerate(ranking, start=1):
        lines.append(
            f"{i}. <b>{rec['distance']:.0f} м</b> (Ур. {rec['level']}: {rec['level_name']})\n"
            f"   <i>Время: {rec['time']}</i>"
        )
    if not ranking:
        lines.append("Нет данных в логе.")
    await message.answer("\n".join(lines), reply_markup=back_kb(), parse_mode="HTML")

@router.message(Command("flight"))
async def cmd_flight(message: Message):
    s = flight_summary()
    if s['sessions'] == 0:
        await message.answer("<b>✈️ Сводка</b>\n\nВ логе пока нет данных.", reply_markup=back_kb(), parse_mode="HTML")
        return
    
    await message.answer(
        f"<b>✈️ Сводка «Чёрного ящика»</b>\n\n"
        f"Всего сессий: {s['sessions']}\n"
        f"Дистанция: {s['total_distance']:.0f} м\n"
        f"Макс. скорость: {s['max_speed']:.2f}\n"
        f"Время: {s['total_time']} сек.",
        reply_markup=back_kb(), parse_mode="HTML",
    )