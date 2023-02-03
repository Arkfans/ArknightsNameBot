import os
import time
import hashlib
import asyncio

import aiohttp


def sign(ts: str = None) -> dict:
    ts = ts or str(int(time.time()))
    signature = hashlib.sha256(f'{os.environ["KEY"]}AN{ts}'.encode('utf-8')).hexdigest()
    return {'timestamp': ts, 'signature': signature}


async def run():
    async with aiohttp.ClientSession() as client:
        async with client.post(os.environ['SERVER'], headers=sign()) as r:
            if r.status == '200':
                print('update alias success')
            else:
                print(f'update alias failed {r.status}')


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(run())
