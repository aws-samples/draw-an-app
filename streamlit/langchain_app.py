# /********************************************************************************************************************
# *  Copyright 2024 Amazon.com, Inc. or its affiliates. All Rights Reserved.                                           *
# *                                                                                                                    *
# *  Licensed under the Amazon Software License (the "License"). You may not use this file except in compliance        *
# *  with the License. A copy of the License is located at                                                             *
# *                                                                                                                    *
# *      http://aws.amazon.com/asl/                                                                                    *
# *                                                                                                                    *
# *  or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES *
# *  OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions    *
# *  and limitations under the License.                                                                                *
# **********************************************************************************************************************/

import os
import json
import boto3
from typing import Dict, List, Any, Union
from pathlib import Path

import langchain
import langchain_community
from langchain.schema.output import LLMResult
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models import BedrockChat
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import load_tools
from langchain_core.output_parsers import JsonOutputParser


from tools.file import FileCreation
from tools.command import GoToWorkspace, RunCommand, set_command_workspace
from chat_state_machine import ChatStateMachine

from botocore.config import Config

config = Config(
    read_timeout=1000,
    retries = {
        'max_attempts': 50,
        'mode': 'standard'
    }
)

print(langchain.__version__)
print(langchain_community.__version__)

# Callback handlder for logging.
class LlmCallbackHandler(BaseCallbackHandler):
    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> Any:
        print(
            f">>>>>>>>>>>>>>>>>>>>>>>>>>LLM Prompt\n{prompts[0]}\n<<<<<<<<<<<<<<<<<<<<<<<<<<LLM Prompt\n"
        )

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> Any:
        print(
            f">>>>>>>>>>>>>>>>>>>>>>>>>>LLM Result\n{response.generations[0][0].text}\n<<<<<<<<<<<<<<<<<<<<<<<<<<LLM Result\n"
        )

    def on_llm_error( self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any) -> Any:
        print(
            f">>>>>>>>>>>>>>>>>>>>>>>>>>LLM Error\n{error, Any}\n<<<<<<<<<<<<<<<<<<<<<<<<<<LLM Error\n"
        )

# Prepare Bedrock LLM.
region = os.environ["BEDROCK_REGION"]
model_id = os.environ["BEDROCK_MODEL_ID"]
model_kwargs = {
    "max_tokens": 2048,
    "temperature": 0,
    "top_k": 1,
    "top_p": 1,
    # "anthropic_version": "bedrock-2023-05-31",
}

max_agent_iterations = 500
verbose_mode = False
parse_errors = True

bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name=region,
    config=config
)


llm = BedrockChat(
    client=bedrock_runtime,
    model_id=model_id,
    provider="anthropic",
    model_kwargs=model_kwargs,
    callbacks=[LlmCallbackHandler()],
).bind(stop=['Human:', '\nObservation:'])

# Prepare tools.
tools = [
    GoToWorkspace,
    RunCommand,
    FileCreation,
    # DuckDuckGoSearchRun(),
] + load_tools(["requests_all"], allow_dangerous_tools=True)

# Prepare chains.
initial_chain = PromptTemplate.from_template(Path(os.path.join(os.path.dirname(__file__), "prompts/initial.txt")).read_text()) | llm | StrOutputParser()
requirements_chain = PromptTemplate.from_template(Path(os.path.join(os.path.dirname(__file__), "prompts/requirements-collection.txt")).read_text()) | llm | StrOutputParser()
migration_scope_chain = PromptTemplate.from_template(Path(os.path.join(os.path.dirname(__file__), "prompts/requirements-collection.txt")).read_text()) | llm | StrOutputParser()

scaffolding_agent = create_react_agent(llm, tools, PromptTemplate.from_template(Path(os.path.join(os.path.dirname(__file__), "prompts/project-scaffolding.txt")).read_text()))
scaffolding_chain = AgentExecutor.from_agent_and_tools(
    agent=scaffolding_agent,
    tools=tools,
    verbose=verbose_mode,
    handle_parsing_errors=parse_errors,
    max_iterations=max_agent_iterations,
)

migrate_application_agent = create_react_agent(llm, tools, PromptTemplate.from_template(Path(os.path.join(os.path.dirname(__file__), "prompts/migrate_application.txt")).read_text()))
migrate_application_chain = AgentExecutor.from_agent_and_tools(
    agent=migrate_application_agent,
    tools=tools,
    verbose=verbose_mode,
    handle_parsing_errors=parse_errors,
    max_iterations=max_agent_iterations,
)


validate_migration_directory_agent = create_react_agent(llm, tools, PromptTemplate.from_template(Path(os.path.join(os.path.dirname(__file__), "prompts/validate_migration_directory.txt")).read_text()))
validate_migration_directory_chain = AgentExecutor.from_agent_and_tools(
    agent=validate_migration_directory_agent,
    tools=tools,
    verbose=verbose_mode,
    handle_parsing_errors=parse_errors,
    max_iterations=max_agent_iterations,
)

modification_agent = create_react_agent(llm, tools, PromptTemplate.from_template(Path(os.path.join(os.path.dirname(__file__), "prompts/project-modification.txt")).read_text()))
modification_chain = AgentExecutor.from_agent_and_tools(
    agent=modification_agent,
    tools=tools,
    verbose=verbose_mode,
    handle_parsing_errors=parse_errors,
    max_iterations=max_agent_iterations,
)

bugfix_agent = create_react_agent(llm, tools, PromptTemplate.from_template(Path(os.path.join(os.path.dirname(__file__), "prompts/bug-fix.txt")).read_text()))
bugfix_chain = AgentExecutor.from_agent_and_tools(
    agent=bugfix_agent,
    tools=tools,
    verbose=verbose_mode,
    handle_parsing_errors=parse_errors,
    max_iterations=max_agent_iterations,
)

git_agent = create_react_agent(llm, tools, PromptTemplate.from_template(Path(os.path.join(os.path.dirname(__file__), "prompts/git-ops.txt")).read_text()))
git_chain = AgentExecutor.from_agent_and_tools(
    agent=git_agent,
    tools=tools,
    verbose=verbose_mode,
    handle_parsing_errors=parse_errors,
    max_iterations=max_agent_iterations,
)

inspection_agent = create_react_agent(llm, tools, PromptTemplate.from_template(Path(os.path.join(os.path.dirname(__file__), "prompts/workspace-inspection.txt")).read_text()))
inspection_chain = AgentExecutor.from_agent_and_tools(
    agent=inspection_agent,
    tools=tools,
    verbose=verbose_mode,
    handle_parsing_errors=parse_errors,
    max_iterations=max_agent_iterations,
)

security_agent = create_react_agent(llm, tools, PromptTemplate.from_template(Path(os.path.join(os.path.dirname(__file__), "prompts/security-scanning.txt")).read_text()))
security_chain = AgentExecutor.from_agent_and_tools(
    agent=security_agent,
    tools=tools,
    verbose=verbose_mode,
    handle_parsing_errors=parse_errors,
    max_iterations=max_agent_iterations,
)

# Create the chat statemachine.
statemachine = ChatStateMachine(llm, json.load(open(os.path.join(os.path.dirname(__file__), "statemachine.json"))), {
    "initial": initial_chain,
    "requirements_collection": requirements_chain,
    "project_scaffolding": scaffolding_chain,
    "project_scaffolding_phase2": modification_chain,
    "project_modification": modification_chain,
    "migration_scope": migration_scope_chain,
    "migrate_application": migrate_application_chain,
    "bug_fix": bugfix_chain,
    "git_ops": git_chain,
    "validate_migration_directory": validate_migration_directory_chain,
    "workspace_inspection": inspection_chain,
    "security_scanning_fixing": security_chain
})

# API functions.
def set_workspace(workspace_path):
    print('set_workspace: ', workspace_path)
    set_command_workspace(workspace_path)

def set_state(state):
    print('set_state: ', state)
    statemachine.set_state(state)

def get_messages():
    print('get_messages:')
    return statemachine.get_messages()

def send_message(message):
    print('send_message: ', message)
    return statemachine.send_message(message)

def get_state():
    print('get_state:')
    return statemachine.get_state()
