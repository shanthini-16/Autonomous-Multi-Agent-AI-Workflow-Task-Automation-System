import math
import json
import statistics
from typing import Dict, Any, List, Optional
import io
import sys

def tool_python_interpreter(code: str, timeout_seconds: int = 5) -> Dict[str, Any]:
    """
    Executes Python code in a safe execution environment.
    Restricts hazardous system imports and provides standard mathematical,
    string, and collection utilities.
    """
    # Safety Check: Disallow unauthorized modules / builtins
    disallowed = ["import os", "import sys", "import subprocess", "import shutil", "open(", "os.", "sys.", "eval(", "exec("]
    for pattern in disallowed:
        if pattern in code:
            raise PermissionError(f"Security Policy Violation: Python code contains forbidden pattern '{pattern}'.")

    # Safe built-in scope
    safe_builtins = {
        "abs": abs, "all": all, "any": any, "bool": bool, "dict": dict,
        "enumerate": enumerate, "filter": filter, "float": float, "int": int,
        "len": len, "list": list, "map": map, "max": max, "min": min,
        "round": round, "set": set, "sorted": sorted, "str": str, "sum": sum,
        "tuple": tuple, "zip": zip, "print": print, "range": range,
        "math": math, "json": json
    }

    # Redirect stdout
    old_stdout = sys.stdout
    redirected_output = io.StringIO()
    sys.stdout = redirected_output

    loc = {}
    try:
        # Execute in sandbox
        exec(code, {"__builtins__": safe_builtins, "math": math, "statistics": statistics}, loc)
        output_str = redirected_output.getvalue().strip()
        
        # Collect exported variables (ignoring functions or private variables)
        clean_vars = {k: v for k, v in loc.items() if not k.startswith("_") and not callable(v)}
        
        return {
            "stdout": output_str,
            "variables": clean_vars,
            "result_summary": output_str if output_str else clean_vars
        }
    except Exception as e:
        raise RuntimeError(f"Python Sandbox Execution Error: {str(e)}")
    finally:
        sys.stdout = old_stdout

def tool_math_evaluator(expression: str = "", operation: str = "", values: Optional[List[float]] = None) -> Dict[str, Any]:
    """
    Performs high-precision mathematical and statistical calculations.
    Operations supported: 'mean', 'median', 'stdev', 'sum', 'min', 'max', 'cagr', 'growth_rate', 'expression'.
    """
    if operation == "expression" or expression:
        # Safe math evaluation using math functions
        safe_dict = {
            "sqrt": math.sqrt, "log": math.log, "log10": math.log10, "exp": math.exp,
            "sin": math.sin, "cos": math.cos, "pow": pow, "abs": abs, "round": round
        }
        # Whitelist characters
        if not all(c in "0123456789+-*/()., eE_sqrtlogxpnca" for c in expression):
            raise ValueError(f"Unsafe characters detected in math expression: {expression}")
        try:
            result = eval(expression, {"__builtins__": None}, safe_dict)
            return {"expression": expression, "result": float(result)}
        except Exception as e:
            raise ValueError(f"Failed to evaluate expression '{expression}': {str(e)}")

    if not values:
        raise ValueError("Values list must be provided for statistical operations.")

    clean_values = [float(v) for v in values]
    if not clean_values:
        raise ValueError("Values list cannot be empty.")

    if operation == "mean":
        res = statistics.mean(clean_values)
    elif operation == "median":
        res = statistics.median(clean_values)
    elif operation == "stdev":
        res = statistics.stdev(clean_values) if len(clean_values) > 1 else 0.0
    elif operation == "sum":
        res = sum(clean_values)
    elif operation == "min":
        res = min(clean_values)
    elif operation == "max":
        res = max(clean_values)
    elif operation == "growth_rate":
        if len(clean_values) < 2 or clean_values[0] == 0:
            raise ValueError("Growth rate requires at least 2 values and non-zero starting base.")
        res = ((clean_values[-1] - clean_values[0]) / clean_values[0]) * 100.0
    elif operation == "cagr":
        # Compound Annual Growth Rate: (End / Begin) ** (1 / n) - 1
        n = len(clean_values) - 1
        if n < 1 or clean_values[0] <= 0:
            raise ValueError("CAGR requires positive initial value and at least 2 periods.")
        res = (((clean_values[-1] / clean_values[0]) ** (1.0 / n)) - 1.0) * 100.0
    else:
        raise ValueError(f"Unsupported operation '{operation}'. Supported: mean, median, stdev, sum, min, max, growth_rate, cagr, expression.")

    return {
        "operation": operation,
        "input_count": len(clean_values),
        "result": round(float(res), 4)
    }

def tool_data_transformer(dataset: List[Dict[str, Any]], action: str, **kwargs) -> Dict[str, Any]:
    """
    Transforms tabular dataset records.
    Actions:
      - 'filter': filter rows by criteria (e.g. status='COMPLETED')
      - 'compute_column': add new column by formula
      - 'aggregate': sum or group by key
      - 'sort': sort by key ascending or descending
    """
    if not isinstance(dataset, list):
        raise TypeError("Dataset must be a list of dictionary records.")

    if action == "filter":
        key = kwargs.get("key")
        value = kwargs.get("value")
        filtered = [row for row in dataset if row.get(key) == value]
        return {
            "action": "filter",
            "initial_count": len(dataset),
            "result_count": len(filtered),
            "data": filtered
        }

    elif action == "compute_column":
        # e.g. total_price = units * unit_price * (1 - discount_rate)
        col_name = kwargs.get("column_name", "computed_metric")
        formula_type = kwargs.get("formula", "net_revenue")
        
        result_rows = []
        for row in dataset:
            new_row = dict(row)
            if formula_type == "net_revenue":
                units = float(row.get("units", 1))
                price = float(row.get("unit_price", 0))
                disc = float(row.get("discount_rate", 0))
                new_row[col_name] = round(units * price * (1.0 - disc), 2)
            result_rows.append(new_row)

        return {
            "action": "compute_column",
            "column_added": col_name,
            "data": result_rows
        }

    elif action == "aggregate":
        group_by = kwargs.get("group_by")
        target_field = kwargs.get("target_field")
        
        aggregates = {}
        for row in dataset:
            group = str(row.get(group_by, "Unknown"))
            val = float(row.get(target_field, 0))
            if group not in aggregates:
                aggregates[group] = {"count": 0, "total": 0.0}
            aggregates[group]["count"] += 1
            aggregates[group]["total"] += val

        for g in aggregates:
            aggregates[g]["average"] = round(aggregates[g]["total"] / aggregates[g]["count"], 2)
            aggregates[g]["total"] = round(aggregates[g]["total"], 2)

        return {
            "action": "aggregate",
            "grouped_by": group_by,
            "aggregates": aggregates
        }

    elif action == "sort":
        key = kwargs.get("key")
        reverse = kwargs.get("reverse", False)
        sorted_data = sorted(dataset, key=lambda x: x.get(key, 0), reverse=reverse)
        return {
            "action": "sort",
            "sorted_by": key,
            "data": sorted_data
        }

    else:
        raise ValueError(f"Unknown transformer action: '{action}'.")
