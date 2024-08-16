import datetime
import tempfile
from os import PathLike
from typing import Any

import firebase_admin
from firebase_admin import credentials, storage

from videoverse_backend.settings import settings


class FirebaseService:
	def __init__(self) -> None:
		cred = credentials.Certificate("creds.json")
		firebase_admin.initialize_app(
			cred,
			{
				"storageBucket": "videoverse-c744a.appspot.com",
			},
		)
		self.bucket = storage.bucket()

	def upload_file(self, file_name: str, file_path: Any) -> None:
		blob = self.bucket.blob(file_name)
		blob.upload_from_filename(file_path)
		blob.generate_signed_url(
			version="v4",
			expiration=datetime.timedelta(minutes=settings.EXPIRATION_TIME),
			method="GET",
		)

	def download_file(self, file_name: str, file_path: str) -> str:
		blob = self.bucket.blob(file_path)
		_, temp_input_path = tempfile.mkstemp(suffix=f".{file_name.split('.')[-1]}")
		blob.download_to_filename(temp_input_path)
		return temp_input_path

	def get_signed_url(self, file_name: str) -> str:
		blob = self.bucket.blob(file_name)
		return blob.generate_signed_url(
			version="v4",
			expiration=datetime.timedelta(minutes=settings.EXPIRATION_TIME),
			method="GET",
		)


firebase_service = FirebaseService()
