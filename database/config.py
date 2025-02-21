from pydantic_settings import BaseSettings, SettingsConfigDict


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
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    @property
    def DATABASE_URL_asyncpg(self) -> str:
        """
        Получение URL для асинхронного подключения к базе данных PostgreSQL (драйвер asyncpg)

        Формат URL:
        postgresql://<DB_USER>/<DB_PASSWORD>@<DB_HOST>:<DB_PORT>/<DB_NAME>
        Returns:
            str: URL для подключения к PostgreSQL
        """
        return f"postgresql+asyncpg://{self.DB_USER}/{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def DATABASE_URL_psycopg(self) -> str:
        """
        Получение URL для синхронного подключения к базе данных PostgreSQL (драйвер psycopg)

        Формат URL:
        postgresql://<DB_USER>:<DB_PASSWORD>@<DB_HOST>:<DB_PORT>/<DB_NAME>
        Returns:
            str: URL для подключения к PostgreSQL
        """
        return f"postgresql+psycopg://{self.DB_USER}/{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file="../.env")


settings = Settings()

