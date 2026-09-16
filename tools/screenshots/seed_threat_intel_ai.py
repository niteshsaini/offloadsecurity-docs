import json, os, sys, urllib.request, io
SP=os.path.dirname(os.path.abspath(__file__))
S=open(f"{SP}/session.txt").read().strip(); B="http://127.0.0.1:8003/api"
def call(method,path,body=None,files=None):
    if files:
        boundary="----docsseed"; buf=io.BytesIO()
        for k,v in (body or {}).items():
            buf.write(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
        for k,(fn,data,ct) in files.items():
            buf.write(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"; filename=\"{fn}\"\r\nContent-Type: {ct}\r\n\r\n".encode()); buf.write(data); buf.write(b"\r\n")
        buf.write(f"--{boundary}--\r\n".encode())
        req=urllib.request.Request(B+path,data=buf.getvalue(),method=method,headers={"Authorization":f"Bearer {S}","Content-Type":f"multipart/form-data; boundary={boundary}"})
    else:
        req=urllib.request.Request(B+path,data=json.dumps(body).encode() if body is not None else None,method=method,headers={"Authorization":f"Bearer {S}","Content-Type":"application/json"})
    try:
        r=urllib.request.urlopen(req,timeout=120); d=json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        d={"http_error":e.code,"body":e.read()[:300].decode(errors="replace")}
    return d
def show(tag,d): print(tag, json.dumps(d)[:220])

# ---- AI Governance: models
models=[
 {"name":"Fraud Scoring Model","description":"Gradient-boosted model scoring card-not-present transactions for fraud risk before authorisation.","owner":"Payments Risk","type":"machine_learning","risk_level":"high","use_case":"Real-time transaction fraud scoring","data_sources":["transaction_history","device_fingerprint","merchant_profile"],"deployment_status":"production","business_unit":"Payments","last_assessment_date":"2026-08-20","next_review_date":"2026-11-20"},
 {"name":"Support Assistant (LLM)","description":"Retrieval-augmented assistant answering customer support tickets from the help-centre corpus; human agent approves every reply.","owner":"Customer Experience","type":"llm","risk_level":"medium","use_case":"Draft replies to support tickets","data_sources":["help_centre_articles","ticket_history"],"deployment_status":"production","business_unit":"Support","last_assessment_date":"2026-07-02","next_review_date":"2026-10-02"},
 {"name":"Loan Pre-qualification","description":"Logistic model producing an indicative pre-qualification decision for personal loan applicants.","owner":"Retail Lending","type":"machine_learning","risk_level":"high","use_case":"Credit pre-qualification","data_sources":["application_form","bureau_score"],"deployment_status":"staging","business_unit":"Lending","next_review_date":"2026-09-30"},
 {"name":"Log Anomaly Detector","description":"Unsupervised model flagging unusual authentication patterns in platform audit logs.","owner":"Security Engineering","type":"machine_learning","risk_level":"low","use_case":"Internal security monitoring","data_sources":["auth_logs"],"deployment_status":"production","business_unit":"Security"},
]
ids={}
existing=call("GET","/ai-governance/models").get("data") or []
for m in models:
    hit=next((e for e in existing if e.get("name")==m["name"]),None)
    d=hit or (call("POST","/ai-governance/models",m).get("data") or {})
    mid=d.get("id") or d.get("model_id"); ids[m["name"]]=mid; print("model",m["name"],mid)
fraud=ids["Fraud Scoring Model"]; loan=ids["Loan Pre-qualification"]; llm=ids["Support Assistant (LLM)"]
if not (call("GET","/ai-governance/risk-assessments").get("data") or []):
    show("ra",call("POST","/ai-governance/risk-assessments",{"model_id":fraud,"assessment_type":"comprehensive","risk_categories":["fairness","privacy","transparency","robustness"],"impact_level":"high","likelihood":"medium","overall_risk_score":72,"mitigation_measures":["Monthly disparate-impact review","Human review of declines above score 0.9","Model card published to Risk Committee"],"conducted_by":"Model Risk Management","next_review_date":"2026-12-01"}))
    show("ra2",call("POST","/ai-governance/risk-assessments",{"model_id":loan,"assessment_type":"pre_deployment","risk_categories":["fairness","transparency"],"impact_level":"high","likelihood":"high","overall_risk_score":81,"mitigation_measures":["Adverse-action reason codes","Bias test before go-live"],"conducted_by":"Model Risk Management","next_review_date":"2026-09-30"}))
if not (call("GET","/ai-governance/bias-tests").get("data") or []):
    show("bias",call("POST","/ai-governance/bias-tests",{"model_id":fraud,"test_name":"Q3 disparate impact — fraud declines","test_type":"demographic_parity","protected_attributes":["age_band","region"],"test_data_source":"August 2026 authorisations (n=1.2M)","baseline_metrics":"Decline rate 2.1% overall","test_results":"Age 18–24: 2.9% (ratio 0.72); Region NE: 2.4% (ratio 0.88)","bias_score":28,"status":"attention_required","recommendations":"Review 18–24 threshold; add velocity features that are not age-correlated."}))
if not (call("GET","/ai-governance/incidents").get("data") or []):
    show("inc",call("POST","/ai-governance/incidents",{"model_id":llm,"incident_title":"Assistant cited a retired refund policy","incident_type":"incorrect_output","severity":"medium","description":"Draft replies referenced the 2024 refund window after the help-centre article was updated; 14 drafts approved before an agent noticed.","detection_method":"Agent report","impact_description":"Customers told a 30-day window instead of 14 days.","affected_users":"14","business_impact":"Goodwill refunds honoured at the stated window.","immediate_actions":"Re-indexed help-centre corpus; added freshness check on retrieved articles.","root_cause_analysis":"Retrieval index refreshed weekly; policy changed mid-week.","lessons_learned":"Index on publish, not on schedule.","reporter_name":"Support Ops","assigned_to":"Customer Experience","status":"resolved","incident_date":"2026-08-28"}))
if not (call("GET","/ai-governance/human-oversight").get("data") or []):
    show("hov",call("POST","/ai-governance/human-oversight",{"model_id":fraud,"decision_id":"txn-88213-decline","decision_context":"High-value card-not-present transaction scored 0.94","ai_recommendation":"Decline","human_decision":"Approve","override_reason":"Cardholder verified by call-back; travelling","decision_rationale":"Score driven by geo-velocity feature; verified benign","confidence_level":"high","review_required":False,"escalation_needed":False,"stakeholders_notified":["fraud-ops"],"decision_maker":"Fraud analyst L2","approval_chain":["L2 analyst"],"audit_notes":"Logged for monthly override review","decision_date":"2026-09-10"}))
if not (call("GET","/ai-governance/training-records").get("data") or []):
    show("train",call("POST","/ai-governance/training-records",{"training_name":"Responsible AI foundations","training_type":"ai_ethics","participant_name":"Priya N.","participant_role":"Data scientist","department":"Payments Risk","training_date":"2026-08-12","duration_hours":3,"completion_status":"completed","assessment_score":92,"certification_earned":True,"trainer_name":"Model Risk Management"}))

# ---- AIBOM reconcile
show("aibom",call("POST","/v1/aibom/scans/sbom",{}))

# ---- Knowledge Base documents
docs=[("Information Security Policy","Policies","policy","""INFORMATION SECURITY POLICY v3.2 — Effective 1 July 2026

1. Purpose. This policy defines how Acme protects the confidentiality, integrity and availability of information assets.
2. Scope. All employees, contractors and systems that store or process Acme information.
3. Access control. Access is granted on least privilege. Multi-factor authentication (MFA) is mandatory for all remote access, all administrative access, and all access to production systems. Shared accounts are prohibited.
4. Password standard. Minimum 14 characters; passphrases encouraged; rotation only on suspected compromise. Password managers are provided.
5. Asset management. All laptops are enrolled in MDM with full-disk encryption. Cloud resources must be tagged with owner and data classification.
6. Logging. Authentication, privileged actions and data exports are logged centrally and retained for 12 months.
7. Vulnerability management. Critical vulnerabilities are remediated within 7 days, high within 30, medium within 90, low within 180.
8. Exceptions. Exceptions require written approval from the CISO, a compensating control and an expiry date not more than 12 months out.
9. Review. This policy is reviewed annually by the Security Steering Committee."""),
("Incident Response Procedure","Procedures","incident_response","""INCIDENT RESPONSE PROCEDURE v2.0

Severity levels: SEV1 (confirmed data breach or production outage), SEV2 (contained compromise, degraded service), SEV3 (suspicious activity, no impact).
Roles: Incident Commander (on-call security lead), Communications Lead, Technical Lead, Scribe.
Timeline: acknowledge within 15 minutes; SEV1 status updates every 30 minutes; initial regulator assessment within 24 hours; DPDP notification to the Data Protection Board within 72 hours of confirming a personal data breach; affected individuals notified without undue delay.
Steps: 1 Detect and triage. 2 Contain — isolate affected hosts, rotate exposed credentials, block indicators. 3 Eradicate — remove persistence, patch root cause. 4 Recover — restore from verified backups, monitor for recurrence. 5 Post-incident review within 5 business days with a blameless write-up.
Evidence: preserve logs and disk images before remediation; chain of custody recorded by the Scribe."""),
("Data Retention Standard","Standards","technical_documentation","""DATA RETENTION STANDARD v1.4

Customer account records: retained for the life of the account plus 7 years.
Transaction records: 8 years (financial regulation).
Support tickets: 3 years.
Security logs: 12 months online, 24 months in cold storage.
Backups: daily for 35 days, monthly for 13 months.
Personal data collected for marketing: deleted 24 months after last interaction or on withdrawal of consent, whichever is first.
Deletion is verified quarterly by Internal Audit; certificates of destruction are kept for 7 years.""")]
have={d.get("title") for d in (call("GET","/knowledge-base/documents").get("data") or [])}
secs={x["name"]:x["id"] for x in (call("GET","/knowledge-base/sections").get("data") or {}).get("sections",[])}
secmap={"Policies":secs.get("Security Policies"),"Procedures":secs.get("Incident Response"),"Standards":secs.get("Technical Documentation")}
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    def pdf(text):
        buf=io.BytesIO(); c=canvas.Canvas(buf,pagesize=A4); w,h=A4; y=h-60
        for line in text.split("\n"):
            for chunk in [line[i:i+95] for i in range(0,max(len(line),1),95)]:
                c.drawString(50,y,chunk); y-=14
                if y<60: c.showPage(); y=h-60
        c.save(); return buf.getvalue()
    mk=lambda t:(pdf(t),"application/pdf",".pdf")
except Exception:
    mk=lambda t:(t.encode(),"text/plain",".txt")
for title,section,dtype,text in docs:
    if title in have: print("kb have",title); continue
    data,ct,ext=mk(text)
    show("kb",call("POST","/knowledge-base/upload",{"title":title,"section_id":secmap[section],"document_type":dtype,"sensitivity_level":"internal","description":f"{title} ({section.lower()})","tags":"security,policy"},files={"file":(title.replace(" ","_")+ext,data,ct)}))

# ---- SOC: triage + auto-fix queue
show("triage",call("POST","/ai-agents/triage/findings",{}))
show("autofix",call("POST","/compliance-engine/remediation/process-findings",{}))
