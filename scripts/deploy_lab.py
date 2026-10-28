"""Build and deploy to an already authorized Skills Network Kubernetes namespace."""
import json
import os
from pathlib import Path
import re
import secrets
import socket
import subprocess
root=Path(__file__).resolve().parents[1]
os.chdir(root)
def run(args,**kwargs):
    return subprocess.run(args,check=True,text=True,**kwargs)
namespace=run(['kubectl','config','view','--minify','-o','jsonpath={..namespace}'],capture_output=True).stdout.strip()
if not re.fullmatch(r'sn-labs-[a-z0-9-]+',namespace):
    raise SystemExit('Select your assigned Skills Network namespace before deploying.')
registry='us.icr.io/'+namespace
# The lab Docker bridge may not inherit working DNS. Resolve the public package
# hosts through the lab resolver and pass normal host mappings into build steps.
build_hosts=[]
for domain in ['registry.npmjs.org','pypi.org','files.pythonhosted.org']:
    build_hosts.extend(['--add-host',domain+':'+socket.gethostbyname(domain)])
for name,directory in [('dealers','server/database'),('sentiment','server/djangoapp/microservices'),('web','server')]:
    image=registry+'/bestcars-'+name+':v1'
    run(['docker','build',*build_hosts,'-t',image,directory])
    run(['docker','push',image])
manifest=json.loads((root/'deploy/kubernetes.json').read_text())
# The lab is disposable: use pod-local demonstration storage where claims are unavailable.
manifest['items']=[x for x in manifest['items'] if x['kind']!='PersistentVolumeClaim']
for item in manifest['items']:
    if item['kind']!='Deployment':continue
    pod=item['spec']['template']['spec'];container=pod['containers'][0]
    name=container['name']
    if name!='mongo':container['image']=registry+'/bestcars-'+name+':v1'
    container['resources']['limits']={'cpu':'500m','memory':'512Mi'}
    if name=='web':
        pod['securityContext']={'fsGroup':1000}
        for var in container['env']:
            if var['name']=='ALLOWED_HOSTS':var['value']='localhost,127.0.0.1,.labs.cognitiveclass.ai,.proxy.cognitiveclass.ai,.skills.network'
    for volume in pod.get('volumes',[]):
        volume.pop('persistentVolumeClaim',None);volume['emptyDir']={}
# Keep the generated runtime secret out of process arguments, logs and source control.
secret={'apiVersion':'v1','kind':'Secret','metadata':{'name':'bestcars-secrets'},'type':'Opaque','stringData':{'django-secret':secrets.token_urlsafe(48)}}
existing=subprocess.run(['kubectl','get','secret','bestcars-secrets','-o','name'],capture_output=True,text=True)
if existing.returncode!=0:run(['kubectl','apply','-f','-'],input=json.dumps(secret))
run(['kubectl','apply','-f','-'],input=json.dumps(manifest))
for name in ['mongo','dealers','sentiment','web']:
    run(['kubectl','rollout','status','deployment/bestcars-'+name,'--timeout=180s'])
run(['kubectl','get','pods'])
print('Deployment ready. Lab data uses disposable emptyDir storage; the base manifest uses persistent claims.')
print('To browse: kubectl port-forward --address 0.0.0.0 service/bestcars-web 8000:8000')
