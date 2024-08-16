from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped
from sqlalchemy.testing.schema import mapped_column

from videoverse_backend.db.models.base import BaseModel


class VideoModel(BaseModel):
	__tablename__ = "video"

	id: Mapped[int] = mapped_column(primary_key=True)
	duration: Mapped[float] = mapped_column(Float, nullable=False)
	path: Mapped[str] = mapped_column(String, nullable=False)
	filename: Mapped[str] = mapped_column(String)
	size: Mapped[float] = mapped_column(Float)
