import threading
import webbrowser

import uvicorn


def open_browser():
    webbrowser.open("http://127.0.0.1:8000/")


def main():
    threading.Timer(1.0, open_browser).start()

    uvicorn.run(
        "backend.app:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )


if __name__ == "__main__":
    main()