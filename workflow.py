from designer_agent import DesignerAgent
from llm_client import LLMClient
from spec_builder import build_openapi, save_spec_yaml
from validator import validate_openapi_spec, mcp_validate_tool
from rich import print
import json
from typing import Dict

def is_api_request(text: str) -> bool: 
    t=text.lower() #Making it lowercase for easier matching
    keywords = ["api", "endpoint", "endpoints", "openapi", "swagger", "rest"]
    return any(k in t for k in keywords) #Looking if it is related to API 

class Workflow:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.agent = DesignerAgent(self.llm)

    def run_interactive(self, user_request: str, out_yaml: str = "openapi_generated.yaml"):
        if not is_api_request(user_request):
            print("[bold red]This tool only supports REST API design.[/]")
            print("Only describe API's you want to make(ex. 'An API to manage student grades').")
            return #Rejecting non API requests
        print("[bold green]1) Requesting initial design from agent...[/]")
        proposal = self.agent.propose(user_request) #Here we get the design proposal from the agent
        print("[bold]Agent proposal (raw):[/]")
        print(json.dumps(proposal, indent=2))

        print("\n[bold cyan]Review the proposal. You can: [enter] to accept, 'edit' to modify JSON, or 'reject' to abort.[/]")
        choice = input("Choice (accept/edit/reject): ").strip().lower() #Read the user decision
        if choice == "accept":
            final = proposal 
        elif choice == "edit":
            print("Paste the entire JSON proposal (single line or multiline). When finished, press enter on a blank line.")
            lines = []
            while True:
                line = input()
                lines.append(line)
                candidate = "\n".join(lines).strip()
                if not candidate:
                    continue
                if line.strip() == "":
                    try:
                        final = parse_json_loose(candidate)
                        break
                    except Exception:
                        print("[bold red]JSON incomplete or invalid. Continue pasting or Ctrl+C to abort.[/]")
                        continue
        else:
            choice == "reject"
            print("Aborted by user.")
            return

        spec = build_openapi(final, title=f"{user_request} API")# Build the OpenAPI spec from the final design
        save_spec_yaml(spec, out_yaml) #Save it to the YAML file
        print(f"[bold]Saved tentative spec to {out_yaml}[/]")
 
        context: Dict = {
            "spec": spec, #The OpenAPI spec
            "user_request": user_request, # The original user request
            "validation": None, # Validation results will go here
        }

        iteration = 0
        while True:
            iteration += 1
            print(f"[bold yellow]MCP-style validation iteration {iteration}...[/]")
            validation_result = mcp_validate_tool(context)
            valid = validation_result["valid"]
            err = validation_result["errors"]

            if valid:
                print(f"[bold green]Spec is valid (after {iteration} validation step(s)).[/]")
                save_spec_yaml(context["spec"], out_yaml) # Save the valid spec
                break
            else:
                print(f"[bold red]Validation failed (iteration {iteration}):[/]")
                print(err) #Print the validation errors to the user
                fix_prompt = f"""The OpenAPI spec failed validation with the following error:\n{err}\n\nHere is the current spec JSON:\n{json.dumps(context["spec"], indent=2)}\n\nPlease produce a corrected OpenAPI 3.0 JSON (only JSON) that fixes the errors. Keep the same endpoints and schemas unless necessary."""
                corrected_raw = self.llm.generate("", fix_prompt, temperature=0.0) #Askign the LLM to fix the spec
                try:
                    corrected = json.loads(corrected_raw)
                except Exception:
                    s = corrected_raw
                    start = s.find("{")
                    end = s.rfind("}")
                    if start != -1 and end != -1:
                        corrected = json.loads(s[start:end+1])
                    else:
                        raise RuntimeError("LLM did not return valid JSON spec.")
                context["spec"] = corrected #Update spec in the MCP context
                save_spec_yaml(context["spec"], out_yaml) #Save the corrected spec
                print(f"[yellow]Wrote corrected spec to {out_yaml}. Re-validating...[/]")
