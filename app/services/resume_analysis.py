import io
import re
import zipfile
from typing import Dict, List, Optional, Tuple

try:
    import PyPDF2  # type: ignore
except ImportError:  # Optional dependency; PDF parsing will be disabled if unavailable
    PyPDF2 = None


# --- Keyword Libraries ---
TITLE_KEYWORDS = [
    "architect",
    "solutions architect",
    "solution architect",
    "cloud architect",
    "enterprise architect",
    "platform architect",
    "technical architect",
    "software architect",
    "lead",
    "manager",
    "director",
    "principal",
    "consultant",
    "engineer",
    "developer",
]

SKILL_NORMALIZATION = {
    "azure": "Microsoft Azure",
    "azure cloud": "Microsoft Azure",
    "aks": "Azure Kubernetes Service (AKS)",
    "event hub": "Azure Event Hubs",
    "cosmos": "Azure Cosmos DB",
    "app services": "Azure App Services",
    "key vault": "Azure Key Vault",
    "api management": "Azure API Management",
    "terraform": "Terraform",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "python": "Python",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "react": "React",
    "node": "Node.js",
    "nodejs": "Node.js",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "microservices": "Microservices",
    "event-driven": "Event-Driven Architecture",
    "distributed systems": "Distributed Systems",
    "ci/cd": "CI/CD",
    "jenkins": "CI/CD",
    "github actions": "CI/CD",
    "api": "API Design",
    "openapi": "API Design",
    "swagger": "API Design",
    "uml": "Architecture Documentation",
    "c4": "Architecture Documentation",
    "governance": "Architecture Governance",
    "roadmap": "Roadmapping",
    "data flow": "Architecture Documentation",
    "sequence diagram": "Architecture Documentation",
    "cloud migration": "Cloud Migration",
    "cloud modernization": "Cloud Modernization",
    "finops": "FinOps",
    "cost optimization": "FinOps",
    "observability": "Observability",
    "monitoring": "Observability",
    "appdynamics": "Observability",
    "splunk": "Observability",
    "security": "Security",
    "zero trust": "Security",
}

SOFT_SKILLS = [
    "leadership",
    "mentoring",
    "coaching",
    "stakeholder management",
    "communication",
    "collaboration",
    "governance",
    "roadmapping",
    "documentation",
    "training",
    "review",
]

DOMAIN_KEYWORDS = ["healthcare", "insurance", "banking", "financial services", "fintech"]

ROLE_LIBRARY = [
    {
        "name": "Azure Solutions Architect",
        "required": ["Microsoft Azure", "Azure Kubernetes Service (AKS)", "Azure App Services", "API Design", "Cloud Migration"],
        "nice": ["CI/CD", "Terraform", "Security", "FinOps"],
        "why": "Deep Azure footprint and history of modernization projects.",
    },
    {
        "name": "Enterprise Architect",
        "required": ["Architecture Governance", "Roadmapping", "Architecture Documentation", "API Design"],
        "nice": ["Security", "FinOps", "Platform Strategy"],
        "why": "Owns standards, roadmaps, and cross-org alignment.",
    },
    {
        "name": "Platform Architect",
        "required": ["Microservices", "Distributed Systems", "API Design", "Kubernetes"],
        "nice": ["Observability", "Security", "FinOps"],
        "why": "Builds reusable platform services and service catalogs.",
    },
    {
        "name": "API / Integration Architect",
        "required": ["API Design", "Event-Driven Architecture", "Microservices"],
        "nice": ["Security", "Observability", "Distributed Systems"],
        "why": "Drives API-first integration and governance.",
    },
    {
        "name": "Cloud Migration Lead",
        "required": ["Cloud Migration", "Cloud Modernization", "Microsoft Azure", "CI/CD"],
        "nice": ["Terraform", "FinOps", "Security"],
        "why": "Leads assessment, planning, and execution of cloud moves.",
    },
]


def _extract_text_from_docx(file_bytes: bytes) -> str:
    with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
        xml = z.read("word/document.xml")
    text = re.sub(r"<[^>]+>", " ", xml.decode("utf-8", errors="ignore"))
    clean = re.sub(r"\s+", " ", text)
    return clean.strip()


def _extract_text_from_pdf(file_bytes: bytes) -> str:
    if PyPDF2 is None:
        raise ValueError("PDF support requires PyPDF2, which is not installed.")
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    pages = []
    for page in reader.pages:
        try:
            pages.append(page.extract_text() or "")
        except Exception:
            continue
    return "\n".join(pages)


def extract_text(file_bytes: bytes, filename: str) -> str:
    name = filename.lower()
    if name.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="ignore")
    if name.endswith(".docx"):
        return _extract_text_from_docx(file_bytes)
    if name.endswith(".pdf"):
        return _extract_text_from_pdf(file_bytes)
    raise ValueError("Unsupported file type. Use PDF, DOCX, or TXT.")


def _normalize_skills(text: str) -> List[str]:
    found = []
    lowered = text.lower()
    for keyword, normalized in SKILL_NORMALIZATION.items():
        if keyword in lowered:
            found.append(normalized)
    return sorted(set(found))


def _extract_titles(text: str) -> List[str]:
    titles = []
    lowered = text.lower()
    for t in TITLE_KEYWORDS:
        if t in lowered:
            titles.append(t.title())
    return sorted(set(titles))


def _extract_soft_skills(text: str) -> List[str]:
    lowered = text.lower()
    return sorted({s for s in SOFT_SKILLS if s in lowered})


def _extract_domains(text: str) -> List[str]:
    lowered = text.lower()
    return sorted({d.title() for d in DOMAIN_KEYWORDS if d in lowered})


def _infer_level(titles: List[str], text: str) -> str:
    lowered = text.lower()
    if any(word in lowered for word in ["principal", "director"]):
        return "Principal/Director"
    if any(word in lowered for word in ["senior", "lead", "architect"]):
        return "Senior/Lead"
    return "Mid"


def _infer_track(text: str) -> str:
    lowered = text.lower()
    if any(word in lowered for word in ["manager", "management", "director"]):
        return "Manager/Leadership"
    if "architect" in lowered:
        return "Architect"
    return "Individual Contributor"


def _score_role(skills: List[str], role: Dict) -> Tuple[int, List[str], List[str]]:
    required = role.get("required", [])
    nice = role.get("nice", [])
    matched = [s for s in required if s in skills]
    gaps = [s for s in required if s not in skills]
    optional_hits = [s for s in nice if s in skills]
    base = (len(matched) / len(required)) * 100 if required else 0
    bonus = 5 * len(optional_hits)
    score = min(100, round(base + bonus))
    return score, matched, gaps


def _build_resume_summary(text: str, titles: List[str], skills: List[str], level: str) -> str:
    headline_title = titles[-1] if titles else "Professional"
    key_skills = ", ".join(skills[:6]) if skills else "modern engineering and cloud"
    return f"{headline_title} with expertise in {key_skills}. Level: {level}."


def _derive_strengths(skills: List[str], soft: List[str], level: str, track: str) -> List[str]:
    strengths: List[str] = []
    if level:
        strengths.append(f"Seniority: {level}")
    if track:
        strengths.append(f"Primary track: {track}")
    if skills:
        strengths.append("Technical breadth: " + ", ".join(skills[:6]))
    if soft:
        strengths.append("Soft skills: " + ", ".join(soft[:4]))
    return strengths


def analyze_resume(text: str, intent: str, user_context: Optional[Dict] = None) -> Dict:
    user_context = user_context or {}
    titles = _extract_titles(text)
    skills = _normalize_skills(text)
    soft = _extract_soft_skills(text)
    domains = _extract_domains(text)
    level = _infer_level(titles, text)
    track = _infer_track(text)

    summary = _build_resume_summary(text, titles, skills, level)
    strengths = _derive_strengths(skills, soft, level, track)

    recommendations = []
    for role in ROLE_LIBRARY:
        score, matched, gaps = _score_role(skills, role)
        recommendations.append(
            {
                "role": role["name"],
                "match": score,
                "why": role["why"],
                "matched": matched,
                "gaps": gaps,
                "nice_to_have": [s for s in role.get("nice", []) if s not in matched],
            }
        )

    recommendations.sort(key=lambda r: r["match"], reverse=True)

    gaps: List[str] = []
    if "Security" not in skills:
        gaps.append("Security architecture (threat modeling, zero trust, compliance).")
    if "FinOps" not in skills:
        gaps.append("Cost optimization / FinOps practices.")
    if track != "Manager/Leadership":
        gaps.append("Leadership signalling: scope of influence, budgeting, stakeholders.")
    if not any(cloud in skills for cloud in ["Amazon Web Services", "Google Cloud", "Microsoft Azure"]):
        gaps.append("Explicit cloud platform depth.")

    action_plan = [
        "Add 3–5 quantified outcomes to recent roles (cost, latency, reliability, adoption).",
        "Highlight architecture artifacts (HLD/LLD, C4 diagrams, runbooks, SLOs).",
        "Call out security and FinOps decisions in past projects.",
        "Reframe platforms/APIs as products with adoption metrics.",
    ]

    next_steps = [
        "Tune LinkedIn/Resume keywords to mirror target roles and ATS filters.",
        "Prepare a portfolio of 2–3 architecture one-pagers with diagrams.",
        "Pursue one credential relevant to gaps (e.g., AZ-305 or AZ-500).",
    ]

    return {
        "summary": summary,
        "titles": titles,
        "skills": skills,
        "soft_skills": soft,
        "domains": domains,
        "level": level,
        "track": track,
        "strengths": strengths,
        "recommendations": recommendations,
        "gaps": gaps,
        "action_plan": action_plan,
        "next_steps": next_steps,
        "intent": intent,
        "user_context": user_context,
    }
