import json
import subprocess
from os import PathLike
from typing import Any

from videoverse_backend.settings import settings


class VideoService:
	@staticmethod
	def get_video_duration(file_path: Any) -> float:
		cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", file_path]
		result = subprocess.run(
			cmd,
			check=True,
			capture_output=settings.DEBUG,
		)
		output = json.loads(result.stdout)
		return float(output["format"]["duration"])

	@staticmethod
	def trim_video(file_path: str, start_time: float | None, end_time: float | None, output_path: str) -> None:
		command = [
			"ffmpeg",
			"-i",
			file_path,
			"-ss",
			str(start_time),
			"-to",
			str(end_time),
			"-c",
			"copy",
			output_path,
		]
		subprocess.run(
			command,
			check=True,
			capture_output=settings.DEBUG,
		)
