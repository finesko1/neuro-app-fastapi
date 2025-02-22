from pydantic_settings import BaseSettings, SettingsConfigDict
from resources.helpers.environment_helper import EnvironmentHelper

env = EnvironmentHelper()

class Settings(BaseSettings):
    """
    Класс Settings используется для хранения конфигурации базы данных.

    Атрибуты:
        DB_HOST (str): Хост базы данных.

        DB_PORT (int): Порт базы данных.

        DB_USER (str): Имя пользователя для подключения к базе данных.

        DB_PASSWORD (str): Пароль для подключения к базе данных.

        DB_NAME (str): Имя базы данных.

    Методы:
        get_database_url() -> str:
            Возвращает строку подключения к базе данных в формате URL.
    Свойства:
        DATABASE_URL_asyncpg (str):
            Возвращает URL для подключения к базе данных с использованием драйвера asyncpg.
        DATABASE_URL_psycopg (str):
            Возвращает URL для подключения к базе данных с использованием драйвера psycopg.

    Этот класс наследует BaseSettings из библиотеки Pydantic,
    что позволяет загружать настройки из переменных окружения или файлов конфигурации.
    """
    DB_HOST_outer: str = "localhost"
    DB_PORT: int = env.db_port
    DB_USERNAME: str = env.db_username
    DB_PASSWORD: str = env.db_password
    DB_NAME: str = env.db_database

    @property
    def DATABASE_URL_asyncpg(self) -> str:
        """
        Получение URL для асинхронного подключения к базе данных PostgreSQL (драйвер asyncpg)

        Формат URL:
            postgresql://<DB_USERNAME>/<DB_PASSWORD>@<DB_HOST>:<DB_PORT>/<DB_NAME>

        Returns:
            str: URL для подключения к PostgreSQL
        """
        return f"postgresql+asyncpg://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST_outer}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def DATABASE_URL_psycopg(self) -> str:
        """
        Получение URL для синхронного подключения к базе данных PostgreSQL (драйвер psycopg)

        Формат URL:
            postgresql://<DB_USERNAME>:<DB_PASSWORD>@<DB_HOST>:<DB_PORT>/<DB_NAME>

        Returns:
            str: URL для подключения к PostgreSQL
        """
        return f"postgresql+psycopg://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST_outer}:{self.DB_PORT}/{self.DB_NAME}"

#localhost, 54321 - локально; postgres + 5432 для доступа из контейнера
settings = Settings(DB_HOST_outer='postgres', DB_PORT=5432)
#settings = Settings(DB_HOST_outer='localhost', DB_PORT=54321)