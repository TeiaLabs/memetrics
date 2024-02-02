import os

import uvicorn

from .settings import Settings


def main():
    print(os.environ)
    settings = Settings()
    uvicorn.run(
        app="memetrics.app:create_app",
        factory=True,
        forwarded_allow_ips="*",
        host=settings.MEME_HOST,
        port=settings.MEME_PORT,
        reload=settings.MEME_RELOAD,
        workers=settings.MEME_WORKERS,
    )


if __name__ == "__main__":
    main()
