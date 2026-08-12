from tools.decision_router import route


def current_context() -> dict:
    return {
        "workload": {"request_rate": 100, "repeated_queries": True},
        "scale": {"concurrency": 4},
        "runtime": {"language": "python", "version": "3.12"},
        "environment": {"os": "linux"},
        "data_semantics": {"mutability": "immutable"},
        "trust_boundary": {"input_trust": "trusted_internal"},
        "failure_model": {"duplicate_delivery_possible": False},
        "compatibility": {"api_version": "v1"},
        "operational_constraints": {"deployment_model": "single_process"},
    }


def candidate() -> dict:
    return {
        "context": {
            "workload": {"request_rate": 100, "repeated_queries": True},
            "scale": {"concurrency": 4},
            "language": "python",
            "runtime_version": "3.12",
            "environment": "linux",
            "trust_boundary": {"input_trust": "trusted_internal"},
        },
        "applicability": {
            "data_semantics": {"mutability": "immutable"},
            "failure_model": {"duplicate_delivery_possible": False},
            "compatibility": {"api_version": "v1"},
        },
        "constraints": {
            "operational": {"deployment_model": "single_process"},
        },
    }


def test_green_exact_context_can_use_fast_route() -> None:
    result = route(current_context(), candidate(), "GREEN")
    assert result["route"] == "FAST"


def test_green_health_does_not_override_critical_mismatch() -> None:
    ctx = current_context()
    ctx["failure_model"]["duplicate_delivery_possible"] = True
    result = route(ctx, candidate(), "GREEN")
    assert result["route"] == "RESEARCH"
    assert result["hard_context_mismatch"] is True


def test_unknown_critical_context_blocks_fast_route() -> None:
    ctx = current_context()
    ctx["trust_boundary"] = {}
    result = route(ctx, candidate(), "GREEN")
    assert result["route"] == "ADAPT"
    assert result["critical_context_unknown"] is True


def test_yellow_health_blocks_fast_even_when_context_matches() -> None:
    result = route(current_context(), candidate(), "YELLOW")
    assert result["route"] == "ADAPT"


def test_red_health_routes_to_research() -> None:
    result = route(current_context(), candidate(), "RED")
    assert result["route"] == "RESEARCH"
