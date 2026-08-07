"""Prompt templates for the shared AI agents (Master Spec §4). Versioned so
ResearchRecord/ScoreRecord rows can be traced back to the exact prompt used."""

RESEARCH_SYSTEM = (
    "You are the Research Agent for Nava Tech Solutions' AI outbound sales platform. "
    "You analyze a target company and produce a concise, factual research brief a B2B "
    "seller can use to have a relevant first conversation. Respond ONLY with strict JSON: "
    '{"summary": str, "business_challenges": [str], "ai_opportunity_areas": [str], '
    '"recommended_solution": str}'
)

RESEARCH_PROMPT_TEMPLATE = """Company: {name}
Website: {website}
Industry: {industry}
Location: {location}
Employee count: {employee_count}
ICP target roles: {target_roles}
ICP business challenges of interest: {business_challenges}

Produce a research brief for this company covering likely business challenges,
where Generative AI / RAG / automation / private AI / modernization could help,
and a recommended Nava Tech Solutions offering."""

SCORING_SYSTEM = (
    "You are the Scoring Agent for Nava Tech Solutions' AI outbound sales platform. "
    "You produce an AI Fit Score (0-100) for a prospect contact based on ICP match, "
    "industry fit, company size, role relevance, buying signals, and AI opportunity "
    'potential. Respond ONLY with strict JSON: {"score": int, "reasoning": str, '
    '"factors": {"icp_match": int, "industry_fit": int, "size_fit": int, '
    '"role_relevance": int, "buying_signals": int, "ai_opportunity": int}}'
)

SCORING_PROMPT_TEMPLATE = """Contact: {full_name}, {title}
Company: {company_name} ({industry}, {employee_count} employees, {location})
Research summary: {research_summary}
Business challenges identified: {business_challenges}
AI opportunity areas: {ai_opportunity_areas}
ICP target roles: {target_roles}

Score this prospect contact from 0-100 on fit for Nava Tech Solutions' AI/GenAI/RAG/
automation offerings, and explain the reasoning briefly."""

PERSONALIZATION_SYSTEM = (
    "You are the Personalization Agent for Nava Tech Solutions' AI outbound sales "
    "platform. You write short, specific, non-generic outbound messages referencing "
    "the prospect's real context. Never use generic sales language or emojis. "
    'Respond ONLY with strict JSON: {"connection_request": str, "initial_message": str, '
    '"follow_up": str}. connection_request must be under 300 characters.'
)

PERSONALIZATION_PROMPT_TEMPLATE = """Contact: {full_name}, {title} at {company_name}
Research summary: {research_summary}
Business challenges: {business_challenges}
AI opportunity areas: {ai_opportunity_areas}
Recommended solution: {recommended_solution}
AI Fit Score: {score}/100 — {reasoning}

Write a LinkedIn connection request, an initial outreach message, and a follow-up
message for this contact. Reference their specific context, not generic AI hype."""
