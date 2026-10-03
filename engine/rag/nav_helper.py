"""Maps user intent keywords to portal routes and action hints."""

_NAV_MAP = [
    # (keywords, route, role, human label, action hint)
    ({"apply", "job", "jobs", "resume", "upload", "seeker", "candidate", "work", "developer", "engineer", "software"},
     "#/seeker", "seeker",
     "Job Seeker Portal",
     "Upload your resume on the Job Seeker Portal to get matched with shortage roles."),

    ({"employer", "hire", "hiring", "talent", "recruit", "recruiting", "sourcing", "company"},
     "#/employer", "employer",
     "Employer Dashboard",
     "Go to the Employer Dashboard to see regional talent supply and hiring feasibility."),

    ({"demand", "posting", "postings", "growth", "high"},
     "#/demand", "policymaker",
     "Demand Analysis",
     "Visit the Demand Analysis page to see occupation-level demand scores across states."),

    ({"supply", "graduate", "graduates", "iti", "training", "capacity", "institute"},
     "#/supply", "policymaker",
     "Supply Estimation",
     "Check the Supply Estimation page for ITI/AISHE graduate output and training capacity."),

    ({"gap", "shortage", "mismatch", "shortages"},
     "#/gap", "policymaker",
     "Gap and Shortages",
     "The Gap and Shortages page shows demand-supply mismatches and shortage risk categories."),

    ({"forecast", "predict", "prediction", "future", "trend", "projection", "projections"},
     "#/forecast", "policymaker",
     "Forecast Explorer",
     "Use the Forecast Explorer for 3/6/12-month demand projections by occupation and state."),

    ({"risk", "critical", "severity", "shap", "explanation"},
     "#/shortage", "policymaker",
     "Shortage Risk",
     "The Shortage Risk page shows calibrated severity with SHAP explanations."),

    ({"policy", "recommendation", "recommendations", "intervention", "interventions", "pmkvy", "budget", "naps", "nats", "dgt"},
     "#/policy", "policymaker",
     "Policy Recommendations",
     "Visit Policy Recommendations for rule-triggered interventions and budgetary estimates."),

    ({"copilot", "ai", "assistant", "chat", "rag"},
     "#/copilot", "policymaker",
     "AI Policy Copilot",
     "Open the AI Policy Copilot page for in-depth conversational analysis."),
]

def get_nav_hints(query: str) -> list:
    """Return portal navigation hints relevant to the query."""
    tokens = set(query.lower().split())
    hints = []
    seen_routes = set()
    for keywords, route, role, label, tip in _NAV_MAP:
        if (tokens & keywords) and route not in seen_routes:
            seen_routes.add(route)
            hints.append({
                "route": route,
                "role": role,
                "label": label,
                "tip": tip,
            })
    return hints[:3]  # At most 3 hints
