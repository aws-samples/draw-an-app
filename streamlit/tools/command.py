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

import subprocess
import time
import os
from langchain.tools import tool

MARKER = "BASH_MARKER"
TIMEOUT_SEC = 60 * 5
WORKSPACE = os.getcwd() +"/workspace"
INTERRUPT_MESSAGE = """
Command interrupted.
It seems your command is either interactive or it never returns. Such commands are not supported by this tool. 
The command was interrupted and the above output may be partial. Please check to be sure that this interruption has not introduced any inconsistencies in your project.
"""

process = subprocess.Popen(
    ["bash"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
)
os.set_blocking(process.stdout.fileno(), False)

def set_command_workspace(path):
    global WORKSPACE
    WORKSPACE = path

    os.makedirs(path, exist_ok=True)

def run(command):
    global process
    process.stdin.write(
        f'{command} \n if [ $? -eq 0 ]; then echo "\nCommand executed."; else echo "\nCommand failed."; fi  \n  echo -n "Current directory is: "; pwd \n echo {MARKER}\n'
    )
    process.stdin.flush()

    start_time = time.time()

    output = ""
    while True:
        line = process.stdout.readline().strip()
        # print(f'line:>{line}<')
        if line == MARKER:
            break

        if len(output) == 0:
            output = line
        else:
            output = output + "\n" + line

        if len(line) == 0:
            time.sleep(1)
        else:
            start_time = time.time()

        if (time.time() - start_time) > TIMEOUT_SEC:
            process.kill()
            process = subprocess.Popen(
                ["bash"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                preexec_fn=os.setsid,
            )
            os.set_blocking(process.stdout.fileno(), False)

            output += INTERRUPT_MESSAGE
            break

    return output


@tool
def RunCommand(command: str) -> str:
    """
    Runs a bash command(non-interactive commands only) and returns the response. It is stateful and retains current directory across multiple invocations.
    This tool however returns only after the command completes. So do not use commands that never returns or use the "&" postfix to run them in async manner. Also do not use it for any commands that expectes further user input interactively.
    You can use this tool with the right commands to check current directory, create, list, edit and delete files and folders, make web requests with curl as well as run any other arbitrary bash commands.

    Do not use the following commands as they are either interactive or very long running:
    1. ls -R
    2. npm start

    If a command fails, it is almost always because you are using incirrect path. When this happens it is better to switch to the workspace folder.


    Args:
        command (str): The bash command to run.

    Returns:
        str: Response from the command. If a command fails, double check your current directory or list the current folder to see where you are currently, and adjust the path used accordingly. Pay attention to the current directory path included in the response as well.
    """

    try:
        return run(command)

    except Exception as e:
        print(e)
        return "Failed to execute."


@tool
def GoToWorkspace(unused: str) -> str:
    """
    This tool lets you switch your current directory to the workspace folder. This tool is extremely useful when you have your commands failing because of path related issues.

    Args:
        Always supply the following string: Unused

    Returns:
      str: Status of the operation and the path of the workspace folder if successful.
    """
    return run(f"cd {WORKSPACE}")
