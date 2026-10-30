from agents import apply_salary_guard

def test_downgrades_hire_when_over_budget():
    d = apply_salary_guard({"recommendation": "Hire"}, 120000, 100000)
    assert d["recommendation"] == "Conditional Hire"
    assert "guard_note" in d

def test_keeps_hire_when_within_budget():
    d = apply_salary_guard({"recommendation": "Hire"}, 90000, 100000)
    assert d["recommendation"] == "Hire"