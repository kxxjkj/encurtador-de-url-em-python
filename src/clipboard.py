"""Acesso à área de transferência do sistema."""

import pyperclip


def copy_to_clipboard(text: str) -> bool:
    """Copia ``text`` para a área de transferência.

    Args:
        text: Texto a ser copiado.

    Returns:
        ``True`` se a cópia funcionou, ``False`` caso o sistema não tenha
        um mecanismo de clipboard disponível (ex.: Linux sem xclip/xsel).
    """
    try:
        pyperclip.copy(text)
        return True
    except pyperclip.PyperclipException:
        return False
