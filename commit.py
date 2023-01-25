import os
import subprocess

from core.constance import base
from datetime import datetime, timezone, timedelta

utc = datetime.utcnow().replace(tzinfo=timezone.utc)
now = utc.astimezone(timezone(timedelta(hours=8)))
time = now.strftime('%y-%m-%d-%H-%M-%S')

subprocess.run('git config --global user.email noreply@arkfans.top', shell=True, cwd=base)
subprocess.run('git config --global user.name MeeBooBot_v0', shell=True, cwd=base)
subprocess.run('git add .', shell=True, cwd=base)
subprocess.run(f'git commit -m \'[UPDATE] Data:{now}-{os.environ["version"]}\'', shell=True, cwd=base)
