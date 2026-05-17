from __future__ import annotations

from functools import lru_cache

import pygame
import qrcode


@lru_cache(maxsize=8)
def make_qr_surface(payload: str, size: int = 132) -> pygame.Surface:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    img = img.resize((size, size))
    return pygame.image.fromstring(img.tobytes(), img.size, img.mode)
