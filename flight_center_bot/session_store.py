import json, os, asyncio

SESSION_FILE = "sessions.json"
_lock = asyncio.Lock()

async def _read_all() -> dict:
    if not os.path.exists(SESSION_FILE):
        return {}
    async with _lock:
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}

async def _write_all(data: dict):
    async with _lock:
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

async def get_session(user_id: int) -> dict:
    data = await _read_all()
    return data.get(str(user_id), {})

async def set_session(user_id: int, session: dict):
    data = await _read_all()
    data[str(user_id)] = session
    await _write_all(data)

async def clear_session(user_id: int):
    data = await _read_all()
    data.pop(str(user_id), None)
    await _write_all(data)