from dataclasses import dataclass
from pathlib import Path

import aiofiles
import yaml


@dataclass
class Files:
    instagram_session_path: Path

    async def load_instagram_session(self) -> dict | None:
        if not self.instagram_session_path.exists():
            return None
        async with aiofiles.open(self.instagram_session_path) as file:
            content = await file.read()
            return yaml.safe_load(content)

    async def save_instagram_session(self, session: dict) -> None:
        async with aiofiles.open(self.instagram_session_path, "w") as file:
            await file.write(yaml.dump(session, default_flow_style=False))
