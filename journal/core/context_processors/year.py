import datetime as dt

from django.http import HttpRequest


def year(request: HttpRequest):
    """Добавляет переменную с текущим годом.

    Returns:
    Tекущий год.
    """
    del request
    return {
        'year': dt.datetime.now().year,
    }
