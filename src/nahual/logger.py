# src/nahual/logger.py

import logging
from typing import Optional


class NahualLogger:
    """Sistema de logging para NahualScript."""

    def __init__(self, debug: bool = False):
        """Inicializa el logger con nivel opcional de debug."""
        self.logger = logging.getLogger('NahualScript')
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(emoji)s %(levelname)s: %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.logger.setLevel(logging.DEBUG if debug else logging.INFO)

        # Emojis para diferentes niveles de log
        self.emojis = {
            'DEBUG': '🔍',
            'INFO': '✨',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'CRITICAL': '💥'
        }

    def _log(self, level: int, msg: str, emoji: Optional[str] = None) -> None:
        """Método interno para manejar el logging con emojis."""
        extra = {'emoji': emoji or self.emojis.get(logging.getLevelName(level), '✨')}
        self.logger.log(level, msg, extra=extra)

    def debug(self, msg: str) -> None:
        """Registra un mensaje de debug."""
        self._log(logging.DEBUG, msg)

    def info(self, msg: str) -> None:
        """Registra un mensaje informativo."""
        self._log(logging.INFO, msg)

    def warning(self, msg: str) -> None:
        """Registra una advertencia."""
        self._log(logging.WARNING, msg)

    def error(self, msg: str) -> None:
        """Registra un error."""
        self._log(logging.ERROR, msg)

    def critical(self, msg: str) -> None:
        """Registra un error crítico."""
        self._log(logging.CRITICAL, msg)

    def lexer_debug(self, token: str, value: str) -> None:
        """Registra información de debug del lexer."""
        self.debug(f"Token encontrado: {token} = {value}")

    def parser_debug(self, rule: str, values: list) -> None:
        """Registra información de debug del parser."""
        self.debug(f"Regla aplicada: {rule} con valores {values}")

    def interpreter_debug(self, operation: str, result: any) -> None:
        """Registra información de debug del intérprete."""
        self.debug(f"Operación: {operation} = {result}")