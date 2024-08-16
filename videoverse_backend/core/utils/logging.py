import logging
import sys
from typing import Any, Union

from loguru import logger

from videoverse_backend.settings import settings


class InterceptHandler(logging.Handler):
	def emit(self, record: logging.LogRecord) -> None:
		try:
			level: Union[str, int] = logger.level(record.levelname).name
		except ValueError:
			level = record.levelno

		frame, depth = logging.currentframe(), 2
		while frame.f_code.co_filename == logging.__file__:
			if frame.f_back:
				frame = frame.f_back
				depth += 1

		logger.opt(depth=depth, exception=record.exc_info).log(
			level,
			record.getMessage(),
		)


LOG_PREFIX_MAPPING = {
	"STAGE": "[STAGE]     ",
	"END STAGE": "[END STAGE] ",
	"GROUP": "[GROUP]     ",
	"END GROUP": "[END GROUP] ",
}


class CustomFormatter:
	def __call__(self, record: dict[str, Any]) -> str:
		stage = record["extra"].get("stage", "")
		log_prefix = LOG_PREFIX_MAPPING.get(stage, "")

		log_format = f"<green>{{time:YYYY-MM-DD HH:mm:ss}}</green>" f"| <level>{log_prefix}{{level: <4}} </level> "
		if record["function"]:
			log_format += "| <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> "
		log_format += "- <level>{message}</level>\n"

		if record["exception"]:
			log_format += "{exception}\n"
		return log_format


def configure_logging() -> None:
	intercept_handler = InterceptHandler()
	intercept_handler.setFormatter(CustomFormatter())  # type: ignore
	logging.basicConfig(
		handlers=[intercept_handler],
		level=logging.NOTSET,
	)

	for logger_name in logging.root.manager.loggerDict:
		if logger_name.startswith("hypercorn."):
			logging.getLogger(logger_name).handlers = []

	hypercorn_logger = logging.getLogger("hypercorn")
	hypercorn_logger.handlers = [intercept_handler]
	hypercorn_logger.propagate = False

	hypercorn_access_logger = logging.getLogger("hypercorn.access")
	hypercorn_access_logger.handlers = [intercept_handler]
	hypercorn_access_logger.propagate = False

	hypercorn_error_logger = logging.getLogger("hypercorn.error")
	hypercorn_error_logger.handlers = [intercept_handler]
	hypercorn_error_logger.propagate = False

	logger.configure(
		handlers=[
			{
				"sink": sys.stdout,
				"level": settings.LOG_LEVEL.value,
				"format": CustomFormatter(),
			},
		],
	)


logger = logger.bind(name="ProductFusion")
stage_logger = logger.bind(stage="STAGE")
end_stage_logger = logger.bind(stage="END STAGE")
