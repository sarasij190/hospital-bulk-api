""" 
BulkProcessor: orchestrates CSV parsing, calls to external API, and final activation.
"""
import csv
import io
import time
from typing import List, Dict, Any
import asyncio
from asyncio import Semaphore

from app.clients.hospital_api import HospitalAPIClient
from app.models import HospitalRowResult

MAX_CONCURRENCY = 5

class BulkProcessor:
    def __init__(self, client: HospitalAPIClient, concurrency: int = MAX_CONCURRENCY):
        self.client = client
        self.semaphore = Semaphore(concurrency)

    async def _create_one(self, row_idx: int, row: Dict[str, str], batch_id: str) -> HospitalRowResult:
        async with self.semaphore:
            name = row.get('name', '').strip()
            address = row.get('address', '').strip()
            phone = row.get('phone', '') or None
            payload = {
                'name': name,
                'address': address,
                'phone': phone,
                'creation_batch_id': batch_id,
            }
            try:
                resp = await self.client.create_hospital(payload)
                hospital_id = resp.get('id')
                return HospitalRowResult(row=row_idx, hospital_id=hospital_id, name=name, status='created')
            except Exception as e:
                return HospitalRowResult(row=row_idx, hospital_id=None, name=name, status='failed', error=str(e))

    async def process_csv_bytes(self, csv_bytes: bytes, batch_id: str) -> Dict[str, Any]:
        start = time.time()
        text = csv_bytes.decode('utf-8')
        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)
        results: List[HospitalRowResult] = []

        tasks = []
        for idx, row in enumerate(rows, start=1):
            tasks.append(self._create_one(idx, row, batch_id))

        # run tasks with concurrency
        completed = await asyncio.gather(*tasks)
        results.extend(completed)

        # Count failures
        failed = sum(1 for r in results if r.status == 'failed')

        # Activate batch only if at least one created
        any_created = any(r.status == 'created' for r in results)
        batch_activated = False
        if any_created:
            try:
                await self.client.activate_batch(batch_id)
                batch_activated = True
            except Exception:
                batch_activated = False

        end = time.time()
        report = {
            'batch_id': batch_id,
            'total_hospitals': len(rows),
            'processed_hospitals': len(rows) - failed,
            'failed_hospitals': failed,
            'processing_time_seconds': round(end - start, 3),
            'batch_activated': batch_activated,
            'hospitals': [r.dict() for r in results]
        }
        return report
