from asyncio.subprocess import Process
from typing import Dict
import asyncio
from core.logger import logger

class ProcessManager:
    def __init__(self):
        self.running: Dict[int, Process] = {}

    def is_running(self, user_id: int) -> bool:
        running = user_id in self.running and self.running[user_id].returncode is None
        logger.debug(f"Check if process running for user {user_id}: {running}")
        return running

    def add(self, user_id: int, proc: Process):
        self.running[user_id] = proc
        logger.info(f"🔄 Добавлен процесс для пользователя {user_id}")

    def remove(self, user_id: int):
        if user_id in self.running:
            logger.info(f"🧹 Удалён процесс пользователя {user_id}")
        self.running.pop(user_id, None)

    async def cancel(self, user_id: int):
        proc = self.running.get(user_id)
        if proc and proc.returncode is None:
            logger.warning(f"⛔ Отмена процесса для пользователя {user_id}")
            proc.kill()
            await proc.wait()
            self.remove(user_id)
            return True
        logger.info(f"ℹ️ Нет активного процесса для пользователя {user_id}")
        return False
