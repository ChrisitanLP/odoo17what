# utils/utils.py
import requests
from requests.exceptions import RequestException, Timeout

def send_request(url, data=None):
    try:
        response = requests.post(url, json=data, timeout=10)  # Establecer un tiempo de espera
        response.raise_for_status()  # Lanza un error para códigos de estado HTTP 4xx/5xx
        return response
    except Timeout:
        # Manejo de errores por tiempo de espera
        print(f"El tiempo de espera para la solicitud a {url} ha expirado.")
        return None
    except RequestException as e:
        # Manejo de errores de red o HTTP
        print(f"Error en la solicitud a {url}: {e}")
        return None

def get_request(url):
    try:
        response = requests.get(url, timeout=10)  # Establecer un tiempo de espera
        response.raise_for_status()  # Lanza un error para códigos de estado HTTP 4xx/5xx
        return response
    except Timeout:
        # Manejo de errores por tiempo de espera
        print(f"El tiempo de espera para la solicitud a {url} ha expirado.")
        return None
    except RequestException as e:
        # Manejo de errores de red o HTTP
        print(f"Error en la solicitud a {url}: {e}")
        return None