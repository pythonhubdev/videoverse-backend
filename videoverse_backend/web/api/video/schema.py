from enum import Enum
from typing import Optional

from videoverse_backend.db.models.base import BaseModel


class TrimType(str, Enum):
	START = "start"
	END = "end"


class TrimSchema(BaseModel):
	video_id: int
	trim_time: Optional[float]
	trim_type: TrimType
	save_as_new: Optional[bool] = False
