"""
Prueba de aislamiento de red (Air-Gap Verification).
Verifica que el contenedor no tenga ruta externa.
"""

import socket
import pytest

def test_external_connectivity_failure():
    """
    Verifica que el sistema falle al intentar alcanzar internet.
    En el entorno internal de Docker, google.com no debe resolverse.
    """
    with pytest.raises(socket.gaierror):
        socket.gethostbyname("google.com")

def test_external_ip_connectivity_failure():
    """
    Verifica que no hay ruta a IPs externas (8.8.8.8).
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    with pytest.raises(socket.timeout):
        s.connect(("8.8.8.8", 53))
    s.close()
