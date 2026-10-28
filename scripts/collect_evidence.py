"""Collect actual read-only API responses from the running lab application."""
import json
from pathlib import Path
import subprocess
root=Path(__file__).resolve().parents[1]
output=root/'.lab-runtime'/'evidence'
output.mkdir(parents=True,exist_ok=True)
checks=[('getdealerreviews','http://127.0.0.1:8000/djangoapp/reviews/dealer/15'),('getalldealers','http://127.0.0.1:8000/djangoapp/get_dealers'),('getdealerbyid','http://127.0.0.1:8000/djangoapp/dealer/15'),('getdealersbyState','http://127.0.0.1:8000/djangoapp/get_dealers/Kansas'),('getallcarmakes','http://127.0.0.1:8000/djangoapp/get_cars')]
for name,url in checks:
    args=['curl','--fail-with-body','--silent','--show-error',url]
    result=subprocess.run(args,capture_output=True,text=True,check=True)
    value=json.loads(result.stdout)
    assert value['status']==200,(name,value)
    text='$ '+' '.join(args)+'\n'+json.dumps(value,indent=2)+'\n'
    (output/(name+'.txt')).write_text(text)
    print(name+': HTTP 200, saved actual cURL response')
args=['curl','--fail-with-body','--silent','--show-error','http://127.0.0.1:5050/analyze/Fantastic%20services']
result=subprocess.run(args,capture_output=True,text=True,check=True)
value=json.loads(result.stdout)
assert value['sentiment']=='positive',value
(output/'analyzereview.txt').write_text('$ '+' '.join(args)+'\n'+json.dumps(value,indent=2)+'\n')
print('analyzereview: positive, saved actual cURL response')
print('Read-only API evidence directory:',output)
