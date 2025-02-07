from utils.config import engine


def test_connection():
    try:
        engine.connect()
        print("Connection successful")
    except Exception as e:
        print("Connection failed")
        print(e)


if __name__ == "__main__":
    test_connection()
