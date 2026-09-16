import json, os, urllib.request
SP=os.path.dirname(os.path.abspath(__file__)); S=open(f"{SP}/session.txt").read().strip(); B="http://127.0.0.1:8003/api"
def call(m,p,b=None):
    req=urllib.request.Request(B+p,data=json.dumps(b).encode() if b is not None else None,method=m,headers={"Authorization":f"Bearer {S}","Content-Type":"application/json"})
    try: return json.loads(urllib.request.urlopen(req,timeout=60).read() or b"{}")
    except urllib.error.HTTPError as e: return {"http_error":e.code,"body":e.read()[:300].decode(errors="replace")}
def safe(d):  # never echo key material
    if isinstance(d,dict): return {k:("<redacted>" if k in ("api_key","key","raw_key","secret","full_key") else safe(v)) for k,v in d.items()}
    if isinstance(d,list): return [safe(x) for x in d]
    return d
# API keys (values shown once by the API are discarded here on purpose)
keys=call("GET","/api-keys"); have={k.get("name") for k in (keys.get("data") or keys.get("keys") or [])}
for name,desc,preset,env,days in [("GitHub Actions — payments-api","Triggers code scans from the release workflow","ci_cd_basic","production",90),("Grafana findings feed","Read-only pull of vulnerabilities and cloud posture into dashboards","read_only","production",180),("Staging pipeline","Full scan control for the staging cluster pipeline","ci_cd_full","staging",30)]:
    if name in have: print("key have",name); continue
    r=call("POST","/api-keys",{"name":name,"description":desc,"scope_preset":preset,"expires_in_days":days,"environment":env})
    print("key",name,json.dumps(safe(r))[:160])
# Teams
teams=call("GET","/teams"); tl=teams.get("data") or teams.get("teams") or teams
names={t.get("name") for t in tl} if isinstance(tl,list) else set()
if "Payments Platform" not in names:
    print("team",json.dumps(call("POST","/teams",{"name":"Payments Platform","description":"Card and UPI payment services — production and staging","organization":"Acme Fintech"}))[:200])
# Invitations into the current team
cur=call("GET","/teams/current"); cur_id=(cur.get("data") or cur).get("id") or (cur.get("data") or cur).get("team_id")
print("current team",cur_id)
for email,role in [("priya.n@offloadsecurity.com","security_analyst"),("rahul.m@offloadsecurity.com","compliance_officer")]:
    print("invite",email,json.dumps(call("POST",f"/teams/{cur_id}/members/invite",{"email":email,"role":role,"message":"Welcome to the security team."}))[:160])
print("members",json.dumps(call("GET",f"/teams/{cur_id}/members"))[:300])
