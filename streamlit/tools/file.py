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

from langchain.tools import tool
import os
import time

@tool
def FileCreation(data: str) -> str:
    """
    This tool can write into files given its absolute path and contents. The parent folder should already exist. It can process only a single file at a time.
    Note that the operation will fail if you provide a relative path.

    Args:
      data (str): A multiline string inside <file></file> where the first line is the absolute file path. File contents start from second line.

      Example:
      <file>
      /usr/projects/game/main.py
      import pygame
      def main_loop():
        print("Running")
      main_loop()
      </file>

    Returns:
      str: The status of the operation.
    """
    try:
        data = data[data.find("<file>") + len("<file>") : data.rfind("</file>")]
        data = data.strip()
        file_path = data[: data.find("\n")]
        contents = data[len(file_path) :]

        # Create directory if it doesn't exist
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(file_path, "w") as file:
            file.write(contents)

        # sleep_time = 10
        # print(f"Sleeping after file creation for {sleep_time} sec ...")
        # time.sleep(sleep_time)
        # print(f"Resuming sleep in file creation after {sleep_time} sec ...")

        return f"File written successfully."
    except Exception as e:
        return "File writing failed."
