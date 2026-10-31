from typing import Dict, Any, List, Optional
import jsonschema

def tool_schema_validator(data: Any, schema: Optional[Dict[str, Any]] = None, required_fields: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Validates data against a standard JSON Schema or a required field checklist.
    """
    errors = []
    
    if schema:
        try:
            jsonschema.validate(instance=data, schema=schema)
        except jsonschema.ValidationError as err:
            errors.append(f"Schema violation at '{'.'.join(str(p) for p in err.path)}': {err.message}")
        except Exception as e:
            errors.append(f"Validation framework error: {str(e)}")

    if required_fields:
        if not isinstance(data, dict):
            errors.append(f"Required fields check expects dictionary, got {type(data).__name__}")
        else:
            for field in required_fields:
                if field not in data or data[field] is None:
                    errors.append(f"Missing mandatory field: '{field}'")

    is_valid = len(errors) == 0
    return {
        "is_valid": is_valid,
        "errors": errors,
        "error_count": len(errors),
        "checked_fields_count": len(required_fields) if required_fields else (len(schema.get("properties", {})) if schema else 0)
    }

def tool_sanity_checker(metrics: Dict[str, Any], bounds: Optional[Dict[str, Dict[str, float]]] = None) -> Dict[str, Any]:
    """
    Validates numeric values against logical real-world boundaries.
    bounds example: {"pe_ratio": {"min": 0, "max": 500}, "percentage": {"min": 0, "max": 100}}
    """
    violations = []
    checked_count = 0

    if not isinstance(metrics, dict):
        return {"passed": False, "violations": ["Metrics payload must be a key-value dictionary."]}

    # Default common sense boundary checks
    for key, val in metrics.items():
        if isinstance(val, (int, float)):
            checked_count += 1
            # Check for NaN / Infinite
            if str(val).lower() in ("nan", "inf", "-inf"):
                violations.append(f"Metric '{key}' has invalid non-finite value: {val}")
                continue

            # Check custom bounds
            if bounds and key in bounds:
                b = bounds[key]
                if "min" in b and val < b["min"]:
                    violations.append(f"Metric '{key}' ({val}) below lower bound ({b['min']})")
                if "max" in b and val > b["max"]:
                    violations.append(f"Metric '{key}' ({val}) exceeds upper bound ({b['max']})")

            # Domain sanity rules
            if "pct" in key.lower() or "percent" in key.lower() or "ratio" in key.lower():
                if val < -100.0 or val > 10000.0:
                    violations.append(f"Unrealistic percentage value for '{key}': {val}%")
            if "latency" in key.lower() and val < 0:
                violations.append(f"Latency cannot be negative: '{key}'={val}ms")

    passed = len(violations) == 0
    return {
        "passed": passed,
        "checked_metrics": checked_count,
        "violations": violations
    }

def tool_consistency_evaluator(claimed_summary: str, factual_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cross-checks claims in synthesized summary against underlying factual data numbers.
    Flags hallucinated numbers or discrepancies.
    """
    anomalies = []
    verified_elements = 0
    text = claimed_summary.lower()

    # Search for occurrences of key values in text
    def scan_dict(d, prefix=""):
        nonlocal verified_elements
        for k, v in d.items():
            if isinstance(v, (int, float)):
                v_str = str(round(v, 2)) if isinstance(v, float) else str(v)
                # If key or value is mentioned, ensure it's accurate
                if k.lower() in text:
                    verified_elements += 1
                    # Check if number appears in reasonable proximity or format
                    if v_str not in text and str(int(v) if isinstance(v, float) else v) not in text:
                        # Allow 1-decimal rounding check
                        one_dec = f"{v:.1f}"
                        if one_dec not in text:
                            anomalies.append(f"Consistency alert: Key '{k}' is mentioned in summary but expected value {v_str} was not found.")
            elif isinstance(v, dict):
                scan_dict(v, prefix=f"{prefix}{k}.")

    scan_dict(factual_data)

    consistency_score = 100.0 if not anomalies else max(0.0, 100.0 - (len(anomalies) * 20.0))
    return {
        "consistent": len(anomalies) == 0,
        "consistency_score": consistency_score,
        "verified_elements": verified_elements,
        "anomalies": anomalies
    }

def tool_output_verifier(task_result: Any, expected_type: str = "any", validation_rules: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Evaluates final output suitability, scoring completeness, schema compliance,
    and sanity. Produces an authoritative verification verdict.
    """
    score = 100.0
    issues = []

    # 1. Non-empty check
    if task_result is None or (isinstance(task_result, (str, list, dict)) and len(task_result) == 0):
        score = 0.0
        issues.append("Result is null or completely empty.")
        return {
            "verified": False,
            "verification_score": 0.0,
            "issues": issues,
            "verdict": "REJECTED"
        }

    # 2. Type compliance
    if expected_type == "dict" and not isinstance(task_result, dict):
        score -= 40.0
        issues.append(f"Expected dictionary result, received {type(task_result).__name__}")
    elif expected_type == "list" and not isinstance(task_result, list):
        score -= 40.0
        issues.append(f"Expected list result, received {type(task_result).__name__}")
    elif expected_type == "number" and not isinstance(task_result, (int, float)):
        score -= 40.0
        issues.append(f"Expected numerical result, received {type(task_result).__name__}")

    # 3. Minimum length / detail check for string syntheses
    if isinstance(task_result, str):
        if len(task_result) < 50:
            score -= 30.0
            issues.append(f"Summary output is insufficiently detailed ({len(task_result)} characters).")

    # 4. Mandatory key checks
    if validation_rules and "required_keys" in validation_rules and isinstance(task_result, dict):
        missing = [k for k in validation_rules["required_keys"] if k not in task_result]
        if missing:
            score -= len(missing) * 20.0
            issues.append(f"Missing required keys: {missing}")

    score = max(0.0, min(100.0, score))
    is_verified = score >= 70.0 and len(issues) == 0

    return {
        "verified": is_verified,
        "verification_score": round(score, 1),
        "issues": issues,
        "verdict": "VERIFIED" if is_verified else "REJECTED",
        "actionable_feedback": issues[0] if issues else "All verification tests passed cleanly."
    }
