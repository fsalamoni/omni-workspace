import json
import os
import aiosqlite
from typing import List, Dict, Any, Optional

class SettingsDB:
    """SQLite-based store for user settings, personal catalog, and agent configs."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            ''')
            await db.commit()

    async def _get_json(self, key: str) -> Optional[Any]:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('SELECT value FROM settings WHERE key = ?', (key,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return json.loads(row[0])
                return None

    async def _set_json(self, key: str, value: Any):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
                (key, json.dumps(value))
            )
            await db.commit()

    async def get_personal_catalog(self) -> List[Dict[str, Any]]:
        catalog = await self._get_json('personal_catalog')
        return catalog if catalog is not None else []

    async def save_personal_catalog(self, models: List[Dict[str, Any]]):
        await self._set_json('personal_catalog', models)

    async def get_agent_configs(self) -> Dict[str, str]:
        configs = await self._get_json('agent_configs')
        return configs if configs is not None else {}

    async def save_agent_configs(self, configs: Dict[str, str]):
        await self._set_json('agent_configs', configs)
