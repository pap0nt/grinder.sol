from asyncio.subprocess import Process
from typing import Dict
import asyncio

class ProcessManager:
    def __init__(self):
        self.running: Dict[int, Process] = {}

    def is_running(self, user_id: int) -> bool:
        return user_id in self.running and self.running[user_id].returncode is None

    def add(self, user_id: int, proc: Process):
        self.running[user_id] = proc

    def remove(self, user_id: int):
        self.running.pop(user_id, None)

    async def cancel(self, user_id: int):
        proc = self.running.get(user_id)
        if proc and proc.returncode is None:
            proc.kill()
            await proc.wait()
            self.remove(user_id)
            return True
        return False
