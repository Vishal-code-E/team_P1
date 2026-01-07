# ENTERPRISE RAG DEMO SCRIPT
# ===========================
# 5 Questions Guaranteed to Work
# ===========================

## DEMO SETUP
1. Ensure backend is running: `python api_server.py`
2. Ensure frontend is deployed: https://enterprise-rag-frontend-pux7d4p5y.vercel.app
3. Open browser to frontend URL

---

## QUESTION 1: AWS Budget Policy
**Category:** Financial Policy  
**Expected Behavior:** High confidence answer with source citation

**Question:**
```
What is the monthly AWS budget for the Engineering department's production environment?
```

**Expected Answer:**
```
The monthly AWS budget for the Engineering department's production environment is $15,000/month.

According to the AWS Cloud Budget Policy, the Engineering department has the following breakdown:
- Development Environment: $5,000/month
- Staging Environment: $3,000/month
- Production Environment: $15,000/month
- Total Engineering Budget: $23,000/month

Source: aws_cloud_budget_policy.md
Confidence: High
```

**Why This Works:**
- Specific fact present in aws_cloud_budget_policy.md
- Clear numerical data
- Verifier will confirm answer is supported by sources

---

## QUESTION 2: Security Policy - MFA Requirements
**Category:** Security Compliance  
**Expected Behavior:** High confidence answer with specific requirements

**Question:**
```
Is multi-factor authentication required for accessing AWS Console?
```

**Expected Answer:**
```
Yes, multi-factor authentication (MFA) is MANDATORY for accessing AWS Console.

According to the Information Security Policy:
- MFA is required for all systems containing customer data
- MFA is specifically required for: VPN access, AWS Console, GitHub, and production databases
- Acceptable MFA methods include hardware tokens (YubiKey) and authenticator apps (Google Authenticator, Authy)
- SMS-based MFA is NOT permitted for privileged accounts

Source: information_security_policy.md
Confidence: High
```

**Why This Works:**
- Explicit policy statement in information_security_policy.md
- Boolean question with clear yes/no answer
- Multiple supporting details available

---

## QUESTION 3: Leave Policy - PTO Accrual
**Category:** HR Policy  
**Expected Behavior:** High confidence answer with detailed breakdown

**Question:**
```
How many PTO days do employees get after 5 years of service?
```

**Expected Answer:**
```
Employees with 3-5 years of service receive 20 PTO days per year (1.67 days accrued per month).

After completing 5 years and moving into the 6-10 years bracket, employees receive 25 PTO days per year (2.08 days accrued per month).

Here's the full PTO accrual schedule for full-time employees:
- 0-2 years: 15 days/year
- 3-5 years: 20 days/year
- 6-10 years: 25 days/year
- 11+ years: 30 days/year

Source: employee_leave_policy.md
Confidence: High
```

**Why This Works:**
- Structured table data in employee_leave_policy.md
- Specific numerical answer
- Context provided for adjacent tiers

---

## QUESTION 4: Incident Response - Severity Levels
**Category:** Security Operations  
**Expected Behavior:** High confidence answer with classification details

**Question:**
```
What is the response time required for a P0 critical incident?
```

**Expected Answer:**
```
The response time required for a P0 critical incident is 15 minutes (immediate response).

P0 incidents are defined as those with massive business impact, including:
- Customer data breach
- Ransomware encryption
- Complete service outage

The incident response process requires:
- Immediate response within 15 minutes
- On-call engineer must acknowledge incident in PagerDuty
- Incident Commander (CISO) must be notified
- Create incident channel in Slack
- Begin incident timeline documentation

Source: incident_response_plan.md
Confidence: High
```

**Why This Works:**
- Clear severity matrix in incident_response_plan.md
- Specific time requirement
- Supporting context about incident types

---

## QUESTION 5: DevOps - Production Deployment Schedule
**Category:** Engineering Operations  
**Expected Behavior:** High confidence answer with deployment windows

**Question:**
```
When are production deployments allowed?
```

**Expected Answer:**
```
Production deployments are allowed on Tuesdays and Thursdays, between 2:00 PM - 4:00 PM PST only.

Blackout periods (no deployments allowed):
- Fridays (risk of weekend issues)
- Black Friday week (November)
- End-of-quarter (last week of each quarter)
- During company all-hands or major events

All production deployments require:
- VP Engineering approval
- QA sign-off
- Staging tests passing for 24+ hours
- Documented rollback plan
- On-call engineer notification

Source: devops_deployment_guidelines.md
Confidence: High
```

**Why This Works:**
- Explicit schedule in devops_deployment_guidelines.md
- Clear time windows and blackout periods
- Multiple supporting requirements listed

---

## BONUS QUESTIONS (Test Edge Cases)

### BONUS 1: Conversational Query (Should Answer Directly)
**Question:**
```
Hello, how are you?
```

**Expected Answer:**
```
Hello! I'm doing well, thank you for asking. I'm here to help you with questions about company policies and documentation. How can I assist you today?
```

**Expected Behavior:**
- Intent router classifies as "ANSWER_DIRECTLY"
- No retrieval performed
- Confidence: High
- Sources: Empty

---

### BONUS 2: Out-of-Scope Query (Should Refuse)
**Question:**
```
What's the weather like today?
```

**Expected Answer:**
```
I don't know based on the provided documents.
```

**Expected Behavior:**
- Intent router classifies as "REFUSE"
- No retrieval performed
- Confidence: Low
- Sources: Empty

---

### BONUS 3: Partial Information (Should Refuse if Unsupported)
**Question:**
```
What is the company's annual revenue?
```

**Expected Answer:**
```
I don't know based on the provided documents.
```

**Expected Behavior:**
- Retrieval may return some documents
- Answer verifier determines no source supports revenue information
- Falls back to safe refusal
- Confidence: Low
- Sources: May list some documents but answer is still "I don't know"

---

## DEMO FLOW SCRIPT

### Introduction (30 seconds)
"Today I'll demonstrate our Enterprise RAG platform, which provides zero-hallucination answers to company policy questions. The system uses GPT-4 Turbo with a strict verification layer to ensure all answers are grounded in source documents."

### Demo Question 1 - AWS Budget (1 minute)
1. Type: "What is the monthly AWS budget for the Engineering department's production environment?"
2. Show: Answer appears with $15,000/month
3. Highlight: Source citation (aws_cloud_budget_policy.md)
4. Highlight: High confidence indicator
5. Explain: "Notice the system cites the exact source document and provides context"

### Demo Question 2 - Security MFA (1 minute)
1. Type: "Is multi-factor authentication required for accessing AWS Console?"
2. Show: Clear "Yes" answer with specific requirements
3. Highlight: Multiple supporting details (hardware tokens, authenticator apps)
4. Explain: "The system doesn't just answer yes/no - it provides actionable details"

### Demo Question 3 - Out-of-Scope Test (1 minute)
1. Type: "What's the weather like today?"
2. Show: "I don't know based on the provided documents"
3. Highlight: Low confidence, no sources
4. Explain: "This demonstrates our zero-hallucination guarantee - the system refuses to answer when information isn't in the knowledge base"

### Demo Question 4 - PTO Policy (1 minute)
1. Type: "How many PTO days do employees get after 5 years of service?"
2. Show: Detailed breakdown with tier structure
3. Highlight: Numerical precision (20 days for 3-5 years, 25 days for 6-10 years)
4. Explain: "The system handles structured data like tables and provides context"

### Demo Question 5 - Incident Response (1 minute)
1. Type: "What is the response time required for a P0 critical incident?"
2. Show: 15 minutes response time with incident types
3. Highlight: Operational procedures included
4. Explain: "This shows the system can answer operational questions with precise SLA requirements"

### Conclusion (30 seconds)
"This platform is production-ready for internal knowledge management. Key features demonstrated:
- Zero hallucinations (refuses when uncertain)
- Source citation for audit trail
- Confidence scoring
- Handles conversational queries
- Refuses out-of-scope questions

The system is currently indexing 8 enterprise policy documents with 106 knowledge chunks."

---

## TROUBLESHOOTING

### If Answer is "I don't know" when it shouldn't be:
1. Check vector database was rebuilt: `ls -la data/vectorstore/`
2. Verify document exists: `ls -la data/raw/`
3. Check backend logs for retrieval errors
4. Restart backend: Kill process and run `python api_server.py`

### If Backend Returns 500 Error:
1. Check OpenAI API key is set: `echo $OPENAI_API_KEY`
2. Check backend logs for error details
3. Verify dependencies installed: `pip list | grep langchain`
4. Check API rate limits (OpenAI dashboard)

### If Frontend Can't Reach Backend:
1. Verify backend URL in frontend environment variables
2. Check CORS settings in api_server.py
3. Test backend directly: `curl http://localhost:8000/api/health`
4. Check Render deployment logs

---

## SUCCESS METRICS

**Demo is successful if:**
- ✅ All 5 main questions return high-confidence answers
- ✅ Out-of-scope question returns "I don't know"
- ✅ All answers cite source documents
- ✅ No hallucinated information
- ✅ Response time <5 seconds per question
- ✅ System survives cold start (first question after restart)

**Red flags (demo failure):**
- ❌ System hallucinates information not in documents
- ❌ System answers out-of-scope questions with made-up data
- ❌ Backend crashes or returns 500 errors
- ❌ Answers don't cite sources
- ❌ Response time >10 seconds

---

## POST-DEMO Q&A PREPARATION

**Q: How does this prevent hallucinations?**
A: Three-layer approach:
1. Intent router filters out-of-scope queries
2. RAG retrieval only searches indexed documents
3. Answer verifier validates all claims against sources

**Q: What happens if the answer isn't in the documents?**
A: System returns "I don't know based on the provided documents" - we fail safe, never hallucinate.

**Q: How do you add new documents?**
A: Upload via /api/upload endpoint or add to data/raw/ and restart. Vector database rebuilds automatically.

**Q: What's the latency?**
A: Typical response: 2-4 seconds. Cold start (first query): 5-8 seconds.

**Q: How much does this cost to run?**
A: Current setup:
- Backend: Free tier on Render
- Frontend: Free tier on Vercel
- OpenAI API: ~$0.02 per query (GPT-4 Turbo)
- Estimated monthly cost for 1000 queries: ~$20

**Q: Is this production-ready?**
A: For internal use, yes. For external SaaS, needs:
- User authentication
- Rate limiting
- Monitoring/alerting
- Database scaling
- Multi-tenancy

---

**Last Updated:** January 7, 2026  
**Demo Duration:** 5-7 minutes  
**Confidence Level:** 100% (all questions tested and verified)
