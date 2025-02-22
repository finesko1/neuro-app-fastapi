"""Класс парсер env"""
import os
import logging
from dotenv import find_dotenv, load_dotenv
from typing import Any, ClassVar, List, Optional

class EnvironmentHelper:
    _instance: ClassVar[Optional["EnvironmentHelper"]] = None

    @property
    def db_host(self) -> str:
        return self._get_env("DB_HOST")

    @property
    def db_port(self) -> int:
        return int(self._get_env("DB_PORT"))

    @property
    def db_database(self) -> str:
        return self._get_env("DB_DATABASE")

    @property
    def db_username(self) -> str:
        return self._get_env("DB_USERNAME")

    @property
    def db_password(self) -> str:
        return self._get_env("DB_PASSWORD")

    @property
    def ollama_model(self) -> str:
        return self._get_env("OLLAMA_MODEL")

    @property
    def ollama_host(self) -> str:
        return self._get_env("OLLAMA_HOST")

    @property
    def ollama_port(self) -> int:
        return int(self._get_env("OLLAMA_PORT"))

    @property
    def ollama_url(self) -> str:
        return self._get_env("OLLAMA_URL")

    @property
    def ollama_connection_timeout(self) -> int:
        return int(self._get_env("OLLAMA_CONNECTION_TIMEOUT"))

    @property
    def ollama_temperature(self) -> float:
        return float(self._get_env("OLLAMA_TEMPERATURE"))

    @property
    def ollama_default_prompt(self) -> str:
        return self._get_env("OLLAMA_DEFAULT_PROMPT")
    
    @property
    def ollama_embedding_model(self) -> str:
        return self._get_env("OLLAMA_EMBEDDING_MODEL")
    

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_env()
        return cls._instance

    def _init_env(self):
        """Инициализирует загрузку переменных окружения из .env файла."""
        env_path = find_dotenv() or os.path.join(os.path.dirname(__file__), '..', '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path)
            logging.info(f"Загружен .env файл из {env_path}")
        else:
            logging.warning("Файл .env не найден! Убедитесь, что файл существует.")

    def _get_env(self, name: str) -> str:
        """
        Возвращает значение переменной окружения.
        
        :param name: Имя переменной окружения.
        :raises ValueError: Если переменная отсутствует.
        :return: Значение переменной окружения.
        """
        value = os.getenv(name)
        if value is None:
            raise ValueError(f"Отсутствует обязательная переменная окружения: {name}")
        return value

    def __getattr__(self, name: str) -> Any:
        """
        Вызывается при попытке обращения к несуществующему атрибуту.
        
        :param name: Имя атрибута.
        :raises AttributeError: Если атрибут не существует.
        """
        raise AttributeError(f"Класс '{self.__class__.__name__}' не имеет атрибута '{name}'. "
                            f"Доступные атрибуты: {list(self.__dir__())}")