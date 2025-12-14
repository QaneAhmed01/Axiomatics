## How to Run the Application

Follow the steps below to install dependencies, configure your environment, and run the AI-powered OpenAPI generator.

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd Axiomatics
```
### 2. Create a Virtural Enviroment

Recommended to isolate all dependencies in a virtual envrioment. Do this by writing the following code in the terminal: 
```bash
python3 -m venv venv
source venv/bin/activate #macOS/Linux
venv\Scripts\activate # Windows
```
### 3. Install all Dependencies
```bash
pip install -r requirements.txt #Put all dependencies in a text file for easy installation
```
### 4. Add Your Own OpenAI API Key
Create a .env.local file and add the key this way:
OPENAI_API_KEY="sk_yourapikeyhere...."

### 5. Run the CLI App
You can now run the tool directly from the terminal with the following command: 
```bash
python3 cli.py "Describe your API here" #Very important that you include the quotation marks
```
Example of this would be:
```bash
python3 cli.py "I want an API to find calories on a burger"
```
### 6. Find the Output File
Step 5 will launch the full workflow, you can find the output at the openapi_generated.yaml file

## Evaluating and Testing the Program

### Workflow testing 
The main testing method was to run the full CLI workflow and verify that all steps behaved correctly from end to end. this included the following behaviors:
- Confirm that valid API requests triggered the agent to  generate resources, endpoints and schemas.
- Review the agent's proposal and verify that the user could either accept, edit or reject the JSON design before c proceeding.
- Ensure that incorrect or malformed JSON insered by the user gave parsing errors.
- Verify that the workflow saved the generated OpenAPI YAML file after each iteration.

### HITL Validation
The HITL logic was tested by just manually interacting with and observing the CLI as follows: 
- If the user accepted it should start the spec creation.
- If the user rejected the proposal we verify that the workflow was terminated.
- If the user chose to edit the JSON proposal from the agent  it was observed if it accepted a correctly formatted JSON and replaced the agents suggestion.
- Lastly check if the MCP context structure updated correctly after each step (proposal -> spec -> validation).

  ### Validation and Iteration Testing
  To verify that the program was able to handle errors and and iterative refinement, several tests were made:
- Providing prompts that intentionally produced invalid OpenAPI specs such as "Hello world".
- Confirming that the OpenAPI validator detected issues and returned error messages.
- Ensured that the system automatically created correct specs using the LLM.
- Re ran the validation in a loop until the spec passed 100% of the checks.
 
  ### Specification Validation
  In this program only the integrated library 'openapi-spec-validator' that is within Python was used. This validator ensured that every generated or corrected OpenAPI document followed the OpenAPI3.0 standard.

## How the System Prompts Guide API Design
The project uses a system of prompts to ensure that the LLM generates consistent and valid REST API designs. The first prompt instruction is for the LLM and is made to be strict intrusctions that shape how the model should propose resources, endpoints and schemas. The system prompt makes it so the best REST practices such as using plural nouns for resources, providing the CRUD style endpoints (Create, Remove, Update and Delete) and creating JSON output only. It also made sure that the agent avoids conversational and/or irrelevant text. 

The second prompt template (the draft prompt) inserts the user's input into a fixed JSON based instruction format. This guides the model to produce a output that directly matches the expected schema. Which is as following: a list of resources, endpoint objects with HTTP methods, paths and JSON schema definitions. The structure of these prompts ensures that the the LLM's outputs are predictable and reduce the risk of malformed or incomplete API designs. All together the system prompt and the draft prompts act as a conststraint that shape the LLM's reasoning and enforce consistency across all generated specifications. 

Last thing to add is that the temperature (Randomness of the LLM outputs) has been set to 0.0 so that no randomness or variance happens. This is to ensure easily said that the same request from a user should always result in the same output from the program. 

## Workflow Design

The program is designed to be a linear, interactive workflow, support HITL validation and iterative specification refinement. The workflow starts by accepting the user's API request through the CLI. Before even processing the request it checks if the input even decribes a API, meaning tht all irrelevant prompts are rejected to keep the workflow soley focused on API design. 

Once the program has deemed the input as a valid request the LLM generates a initial proposal that contains resources, endpoints and schemas. The user then reviews this proposal and can either accept it, edit the JSON manually or reject the workflow completely. After a proposal is either accepted or edited, the system converts it into a OpenAPI specification and saves it as a YAML file.

The generated specification is then validated using a OpenAPI validator. If the spec is invalid the system constructs a error prompt and asks the LLM to generate a corrected version. This updated spec is then stored in the shared MCP style context and re-validated. This loop keeps going until the validator confirms the the specifications is fully correct. 






