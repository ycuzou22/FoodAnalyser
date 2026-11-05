"""Identifiants UUID version 7 (RFC 9562).

Un UUID v7 commence par l'horodatage en millisecondes : les clés insérées se suivent dans
l'index B-tree (moins de fragmentation qu'un UUID v4) tout en restant non devinables
(74 bits aléatoires), ce qui protège contre l'énumération des ressources (anti-IDOR).

Python 3.14 fournira `uuid.uuid7()` ; cette implémentation sert d'ici là.
"""

import os
import time
import uuid

_RAND_A_BITS = 12
_RAND_B_BITS = 62


def uuid7() -> uuid.UUID:
    timestamp_ms = time.time_ns() // 1_000_000
    random_bits = int.from_bytes(os.urandom(10), "big")
    rand_a = random_bits >> (80 - _RAND_A_BITS)
    rand_b = random_bits & ((1 << _RAND_B_BITS) - 1)

    value = (timestamp_ms & ((1 << 48) - 1)) << 80
    value |= 0x7 << 76  # version
    value |= rand_a << 64
    value |= 0b10 << 62  # variant RFC 9562
    value |= rand_b
    return uuid.UUID(int=value)
