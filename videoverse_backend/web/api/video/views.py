from fastapi import APIRouter, File, UploadFile

from videoverse_backend.core import DEFAULT_ROUTE_OPTIONS, APIResponse, CommonResponseSchema
from videoverse_backend.web.api.video.controller import VideoController
from videoverse_backend.web.api.video.schema import TrimSchema

video_router = APIRouter(prefix="/video", tags=["Video"])


@video_router.post(
	"/upload",
	summary="Upload a video file with maximum size of 25MB",
	**DEFAULT_ROUTE_OPTIONS,
)
async def upload_video(file: UploadFile = File(...)) -> APIResponse:
	return await VideoController.upload_video(file)


@video_router.get(
	"/list",
	summary="List all videos",
	**DEFAULT_ROUTE_OPTIONS,
)
async def list_videos() -> APIResponse:
	return await VideoController.list_videos()


@video_router.post(
	"/trim",
	summary="Trim a video",
	**DEFAULT_ROUTE_OPTIONS,
)
async def trim_video(body: TrimSchema) -> APIResponse:
	return await VideoController.trim_video(body)
