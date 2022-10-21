from dataclasses import dataclass
from typing import Optional


@dataclass
class RemoteUser:
    id: int
    session: Optional[str]
