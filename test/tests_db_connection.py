import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.config import engine


def test_db_connection():
    try:
        engine.connect()
        print("Connection Successful")
    except Exception as e:
        print("Connection Failed")
        print(e)


if __name__ == "__main__":
    test_db_connection()
