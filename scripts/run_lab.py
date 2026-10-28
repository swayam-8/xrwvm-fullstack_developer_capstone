"""Run the capstone in the disposable Skills Network lab without Docker."""
import os
import secrets
import subprocess
import sys
import time
from pathlib import Path
root = Path(__file__).resolve().parents[1]
os.chdir(root)
runtime = root / '.lab-runtime'
runtime.mkdir(exist_ok=True)
env = os.environ.copy()
secret = runtime / 'django-secret'
if not secret.exists():
    secret.write_text(secrets.token_urlsafe(48))
    secret.chmod(0o600)
env['DJANGO_SECRET_KEY'] = secret.read_text().strip()
env['ALLOWED_HOSTS'] = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1,.labs.cognitiveclass.ai')
env['backend_url'] = 'http://127.0.0.1:3030'
env['sentiment_analyzer_url'] = 'http://127.0.0.1:5050'
python = root / '.venv/bin/python'
def run(args): subprocess.run([str(x) for x in args],check=True,env=env)
if not python.exists():
    try:
        run([sys.executable,'-m','venv','.venv'])
    except subprocess.CalledProcessError:
        run([sys.executable,'-m','pip','install','--user','virtualenv'])
        run([sys.executable,'-m','virtualenv','--clear','.venv'])
run([python,'-m','pip','install','-r','server/requirements.txt','-r','server/djangoapp/microservices/requirements.txt'])
run(['npm','ci','--prefix','server/frontend'])
run(['npm','run','build','--prefix','server/frontend'])
run(['npm','ci','--prefix','server/database'])
run([python,'server/manage.py','migrate','--noinput'])
run([python,'server/manage.py','seed_cars'])
run([python,'server/manage.py','collectstatic','--noinput'])
run([python,'server/manage.py','test','djangoapp'])
run([python,'-m','unittest','discover','-s','server/djangoapp/microservices','-p','test_sentiment.py'])
def start(name,args,cwd=root):
    log=(runtime/(name+'.log')).open('a')
    process=subprocess.Popen([str(x) for x in args],cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    (runtime/(name+'.pid')).write_text(str(process.pid))
    return process
mongo_data=runtime/'mongo';mongo_data.mkdir(exist_ok=True)
start('mongo',['mongod','--dbpath',mongo_data,'--bind_ip','127.0.0.1','--port','27017'])
time.sleep(3)
run(['npm','test','--prefix','server/database'])
start('dealers',['node','app.js'],root/'server/database')
start('sentiment',[python,'-m','gunicorn','app:app','--bind','0.0.0.0:5050'],root/'server/djangoapp/microservices')
start('web',[python,'manage.py','runserver','0.0.0.0:8000','--noreload'],root/'server')
print('Services started. Use Launch Application on port 8000. Logs: .lab-runtime/*.log')
