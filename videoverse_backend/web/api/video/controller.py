import os
import subprocess
import tempfile as sync_tempfile
from contextlib import contextmanager
from typing import Any, Optional
from uuid import uuid4

from aiofiles import tempfile
from fastapi import UploadFile
from fastapi.encoders import jsonable_encoder
from starlette import status

from videoverse_backend.core import APIResponse, StatusEnum, logger
from videoverse_backend.dao import VideoDAO
from videoverse_backend.db import VideoModel
from videoverse_backend.services import FileService, VideoService
from videoverse_backend.services.firebase_service import firebase_service
from videoverse_backend.settings import settings
from videoverse_backend.web.api.video.schema import TrimSchema, TrimType


class VideoController:
	@staticmethod
	@contextmanager
	def manage_temp_file(suffix: str) -> Any:  # type: ignore
		fd: Optional[int] = None
		path: Optional[str] = None
		try:
			fd, path = sync_tempfile.mkstemp(suffix=suffix)
			yield path
		finally:
			os.close(fd) if fd else None
			os.unlink(path) if path else None

	@staticmethod
	async def upload_video(file: UploadFile) -> APIResponse:
		try:
			file_size = FileService.get_file_size(file)
			if file_size > settings.MAX_FILE_SIZE:
				return APIResponse(
					status_=StatusEnum.ERROR,
					message=f"File size must be less than {settings.MAX_FILE_SIZE}MB",
					status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
				)

			async with tempfile.NamedTemporaryFile(delete=False) as temp_file:
				await temp_file.write(await file.read())
				temp_file_path = temp_file.name

			duration = VideoService.get_video_duration(temp_file_path)
			if not (settings.MIN_DURATION <= duration <= settings.MAX_DURATION):
				logger.info(f"Removing video since it's duration is {duration}")
				os.unlink(temp_file_path)  # type: ignore
				return APIResponse(
					status_=StatusEnum.ERROR,
					message=f"Video duration must be between {settings.MIN_DURATION} and {settings.MAX_DURATION} "
					f"seconds",
					status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
				)

			firebase_path = f"videos/{file.filename}_{uuid4()}"
			firebase_service.upload_file(firebase_path, temp_file_path)

			await VideoDAO().create(  # type: ignore
				{
					"filename": file.filename,
					"path": firebase_path,
					"duration": duration,
					"size": file_size,
				},
			)

			return APIResponse(
				status_=StatusEnum.SUCCESS,
				message="Video uploaded successfully",
				status_code=status.HTTP_201_CREATED,
			)
		except Exception as exception:
			logger.error(f"Error while uploading video: {exception}")
			return APIResponse(
				status_=StatusEnum.ERROR,
				message="Error while uploading video",
				data={"error": str(exception)},
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			)

	@staticmethod
	async def list_videos() -> APIResponse:
		try:
			videos = await VideoDAO().get_all()  # type: ignore
			return APIResponse(
				status_=StatusEnum.SUCCESS,
				message="List of videos",
				data=jsonable_encoder(videos),
			)
		except Exception as exception:
			logger.error(f"Error while listing videos: {exception}")
			return APIResponse(
				status_=StatusEnum.ERROR,
				message="Error while listing videos",
				data={"error": str(exception)},
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			)

	@staticmethod
	async def trim_video(body: TrimSchema) -> APIResponse:
		video: VideoModel = await VideoDAO.get(body.video_id)  # type: ignore
		if not video:
			return APIResponse(
				status_=StatusEnum.ERROR,
				message="The video you are trying to trim does not exist",
				status_code=status.HTTP_404_NOT_FOUND,
			)

		start_time, end_time = (
			(body.trim_time, video.duration) if body.trim_type == TrimType.START else (0, body.trim_time)
		)

		if not (0 < start_time < end_time):  # type: ignore
			return APIResponse(
				status_=StatusEnum.ERROR,
				message="Invalid trim value, start time must be greater than 0 and less than the video duration",
				status_code=status.HTTP_400_BAD_REQUEST,
			)

		temp_file_path = firebase_service.download_file(video.filename, video.path)
		with VideoController.manage_temp_file(suffix=f".{video.filename.split('.')[-1]}") as temp_output_path:
			try:
				VideoService.trim_video(temp_file_path, start_time, end_time, temp_output_path)
				new_duration = end_time - start_time  # type: ignore
				new_size = os.path.getsize(temp_output_path) / (1024 * 1024)

				if body.save_as_new:
					trimmed_filename = f"trimmed_{uuid4()}_{video.filename}"
					firebase_path = f"videos/{trimmed_filename}"
					firebase_service.upload_file(firebase_path, temp_output_path)
					await VideoDAO().create(  # type: ignore
						{
							"filename": trimmed_filename,
							"path": firebase_path,
							"duration": new_duration,
							"size": new_size,
						},
					)

					return APIResponse(
						status_=StatusEnum.SUCCESS,
						message="Video trimmed and saved as a new copy successfully",
						status_code=status.HTTP_200_OK,
					)
				else:
					firebase_service.upload_file(video.path, temp_output_path)
					await VideoDAO().update(  # type: ignore
						video.id,
						{
							"duration": new_duration,
							"size": new_size,
						},
					)

					return APIResponse(
						status_=StatusEnum.SUCCESS,
						message="Video trimmed and updated successfully",
						status_code=status.HTTP_200_OK,
					)

			except subprocess.CalledProcessError as e:
				logger.error(f"Error during video trimming: {e}")
				return APIResponse(
					status_=StatusEnum.ERROR,
					message="Error while trimming video",
					status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
				)
