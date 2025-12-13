from openapi_spec_validator import validate_spec
from typing import Dict, Any 

def validate_openapi_spec(spec_dict):
    try:
        validate_spec(spec_dict)  
        return True, None
    except Exception as e:
        return False, str(e)
    
def mcp_validate_tool(context: Dict[str, Any]) -> Dict[str, Any]:
    spec = context["spec"]
    valid, err = validate_openapi_spec(spec)
    result = {
        "valid": valid,
        "errors": err,
    }
    context["validation"] = result
    return result