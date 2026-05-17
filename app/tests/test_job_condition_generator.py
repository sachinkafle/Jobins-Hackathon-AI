from app.services.job_condition_generator import generate_conditions


def test_generate_conditions_splits_mandatory_and_welcome() -> None:
    description = """
Requirements:
- 4+ years accounting experience
- CPA certification preferred
- Auditing experience is a plus
Responsibilities:
- Prepare reports
"""

    app_cond, welcome_cond = generate_conditions(description)

    assert "4+ years accounting experience" in app_cond
    assert "CPA certification preferred" in welcome_cond
    assert "Auditing experience is a plus" in welcome_cond


def test_generate_conditions_fallback_for_empty_welcome() -> None:
    description = """
Requirements:
- 3+ years of payroll accounting
- Strong Excel skill
"""

    app_cond, welcome_cond = generate_conditions(description)

    assert "payroll accounting" in app_cond
    assert "preferred" in welcome_cond.lower()

