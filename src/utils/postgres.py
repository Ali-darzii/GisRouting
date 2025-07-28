def prepare_connection_string(host: str, port: str, username: str, password: str, db: str) -> str:
    return "postgresql+psycopg2://{}:{}@{}:{}/{}".format(username, password, host, port, db)