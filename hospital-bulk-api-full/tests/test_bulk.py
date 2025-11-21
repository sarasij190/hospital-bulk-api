import pytest
from httpx import AsyncClient
from fastapi import status
from app.main import app
import respx
from httpx import Response
import os

HOSP_BASE = os.getenv('HOSPITAL_API_BASE', 'https://hospital-directory.onrender.com')

CSV_SMALL = """name,address,phone
A Hospital,1 Road,555-1111
B Clinic,2 Road,
"""

@respx.mock
@pytest.mark.asyncio
async def test_bulk_success(monkeypatch):
    # mock create hospital responses
    create_route = respx.post(f"{HOSP_BASE}/hospitals/").mock(return_value=Response(201, json={"id": 101}))
    activate_route = respx.patch(f"{HOSP_BASE}/hospitals/batch/some-batch-id/activate").mock(return_value=Response(200, json={"activated": True}))

    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        files = {'file': ('hosp.csv', CSV_SMALL, 'text/csv')}
        resp = await ac.post('/hospitals/bulk', files=files)
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data['total_hospitals'] == 2
        assert data['failed_hospitals'] == 0
        assert 'batch_id' in data
