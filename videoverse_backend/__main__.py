from videoverse_backend.web.application import get_app
from videoverse_backend.web.hypercorn_app import HypercornApplication


def main() -> None:
	"""Entrypoint of the application."""
	app = get_app()
	hypercorn_app = HypercornApplication(app)
	hypercorn_app.run()


if __name__ == "__main__":
	main()
