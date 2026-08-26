import requests

from isimip_qc.config import settings


def confirm_isimip_id(isimip_id):
    response = requests.post(f'{settings.DATA_URL}/api/v1/ids/', json=[str(isimip_id)])
    response.raise_for_status()
    return response.json()
