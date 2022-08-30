from plyer import notification
import sys


def notify(title, message):
    # notification.notify(title=title, message=message, app_icon="Paomedia-Small-N-Flat-Bell.ico")
    notification.notify(title=title, message=message)


if __name__ == "__main__":
    title = "hello world"
    if len(sys.argv) > 1:
        title = sys.argv[1]

    message = "this is a message"
    if len(sys.argv) > 2:
        message = sys.argv[2]
    notify(title, message)
