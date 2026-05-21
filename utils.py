"""
Módulo utilitário com helpers e decoradores para performance.
"""

from typing import Callable, Any, TypeVar, Optional
from functools import wraps
import time
import logging

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


def medir_tempo(func: F) -> F:
    """
    Decorador para medir tempo de execução.
    
    Exemplo:
        @medir_tempo
        def processar_dados():
            ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        resultado = func(*args, **kwargs)
        tempo = time.time() - start
        logger.info(f"{func.__name__} executado em {tempo:.3f}s")
        return resultado
    
    return wrapper


def validar_nao_vazio(campo: str):
    """
    Decorador para validar que campo não está vazio.
    
    Exemplo:
        @validar_nao_vazio('labels')
        def processar(labels):
            ...
    """
    def decorador(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            valor = kwargs.get(campo) or (args[0] if args else None)
            if not valor:
                raise ValueError(f"Campo '{campo}' não pode estar vazio")
            return func(*args, **kwargs)
        return wrapper
    return decorador


def cache_resultado(ttl_segundos: int = 3600):
    """
    Decorador para cachear resultado por tempo.
    
    Exemplo:
        @cache_resultado(ttl_segundos=3600)
        def carregar_dados():
            ...
    """
    def decorador(func: F) -> F:
        cache = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            agora = time.time()
            chave = (args, tuple(sorted(kwargs.items())))
            
            if chave in cache:
                resultado, tempo_cache = cache[chave]
                if agora - tempo_cache < ttl_segundos:
                    return resultado
            
            resultado = func(*args, **kwargs)
            cache[chave] = (resultado, agora)
            return resultado
        
        return wrapper
    return decorador
