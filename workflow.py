from designer_agent import DesignerAgent
from llm_client import LLMClient
from spec_builder import build_openapi, save_spec_yaml
from validator import validate_openapi_spec, mcp_validate_tool
from rich import print
import json
from typing import Dict

class Workflow:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.agent = DesignerAgent(self.llm)

    def run_interactive(self, user_request: str, out_yaml: str = "openapi_generated.yaml"):
        print("[bold green]1) Requesting initial design from agent...[/]")
        proposal = self.agent.propose(user_request)
        print("[bold]Agent proposal (raw):[/]")
        print(json.dumps(proposal, indent=2))

        print("\n[bold cyan]Review the proposal. You can: [enter] to accept, 'edit' to modify JSON, or 'reject' to abort.[/]")
        choice = input("Choice (accept/edit/reject): ").strip().lower()
        if choice == "accept":
            final = proposal
        elif choice == "edit":
            print("Paste the entire JSON proposal (single line or multiline). End input with a blank line.")
            lines = []
            while True:
                line = input()
                if line.strip() == "":
                    break
                lines.append(line)
            text = "\n".join(lines)
            final = json.loads(text)
        else:
            choice == "reject"
            print("Aborted by user.")
            return

        spec = build_openapi(final, title=f"{user_request} API")
        save_spec_yaml(spec, out_yaml)
        print(f"[bold]Saved tentative spec to {out_yaml}[/]")
 
        context: Dict = {
            "spec": spec,
            "user_request": user_request,
            "validation": None,
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
                save_spec_yaml(spec, out_yaml)
                break
            else:
                print(f"[bold red]Validation failed (iteration {iteration}):[/]")
                print(err)
                fix_prompt = f"""The OpenAPI spec failed validation with the following error:\n{err}\n\nHere is the current spec JSON:\n{json.dumps(spec, indent=2)}\n\nPlease produce a corrected OpenAPI 3.0 JSON (only JSON) that fixes the errors. Keep the same endpoints and schemas unless necessary."""
                corrected_raw = self.llm.generate("", fix_prompt, temperature=0.0)
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
                spec = corrected
                save_spec_yaml(spec, out_yaml)
                print(f"[yellow]Wrote corrected spec to {out_yaml}. Re-validating...[/]")

# ===== Top-level script to run workflow =====
if __name__ == "__main__":
    # Initialize LLM client
    llm = LLMClient(provider="openai", model="gpt-4o-mini")

    # Create workflow
    wf = Workflow(llm)

    # Ask user for a prompt
    user_request = input("Describe the API you want to generate: ")

    # Run interactive workflow
    wf.run_interactive(user_request)
