# examples/basic_usage.py
from alfacrm import ALFACRM  # больше не нужно указание src в пути

hostname = "codo.s20.online"
email = "xmarta@yandex.ru"
key = "a4af59d2-fd7d-11ee-b9b8-3cecefbdd1ae"

api = ALFACRM(hostname, email, key)
