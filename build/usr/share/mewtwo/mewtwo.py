#!/usr/share/mewtwo/mewtwo-env/bin/python3

import sys
import os
import openai
from openai import OpenAI
from openai.types import CompletionUsage
from openai.types.chat import ChatCompletion, ChatCompletionMessage,ChatCompletionMessageToolCall
from openai.types.chat.chat_completion_message_tool_call import Function
from openai.types.chat.chat_completion import Choice
from src import tools 
from src import functions
from src import database
from src import documentReader

def respond_to_chat(chat_id,attempt = 0):
    
    docsPath = "/usr/share/mewtwo/Documentation/"

    database.initialize_user_db()
    config = database.get_config()
    client = OpenAI(
        api_key=config['openai_api_key'],
        organization=config['openai_org_id']
    ) 
    instructions = f'''
Your name is Mewtwo. You are an Ai assistant for server administrators. Here is some information about the server instance:

OS Information:
```
{config.get('os_info')}
```

User's current directory: {os.getcwd()}

You can run commands for the user using the `run_commands` tool. Include each command you wish to run in a list, for example `['pwd','ln -s']`. When asked to find files, only search in the user's current directory unless specifically asked to search within subdirectories.
For example, if asked which files are older than one week but not older than two weeks, you would restrict your search to the current directory:
```
find . -maxdepth 1 -type f -mtime +7 -mtime -14
```

You can answer a user's questions about the server by searching through the documentation using `search_documentation`. Provide a descriptive `query_text`.

You can retrieve text from documentation using the `documentReader` tool by providing a filepath. If search results yield information and you would like to retrieve more context, include the `filepath` returned by the `search_documentation` in the `documentReader` to retrieve the whole document.

Server documentation is located at `{docsPath}`. Here is the directory tree:
```
{functions.get_directory_tree(docsPath)}
```
You can access documentation using the `documentReader` tool to obtain more relevant and detailed information. Use the documentation to answer the user's questions.
You can also use the `documentReader` to read other kinds of files, like .py python scripts, .sh shell scripts, and more. This will allow you to analyze the code base and answer questions about it.
If the user asks why documentation is missing, remind them that they must run `mewtwo-setup rag` to update the vector database used for retrieval-augmented generation.
'''
    
    instructions_jsonl = [{'role': 'system','content': instructions}]
    results = database.get_chat_history(limit = 6)
    messages = []
    for row in results:
        messages.append(eval(row[1]))

    messages = instructions_jsonl + messages 
    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model= 'gpt-4o-mini',
            tools = tools.tools,
            temperature=0.8
        )
    except openai.BadRequestError as e:
        user_json = database.get_chat_message(chat_id)
        database.clear_chat_history()
        chat_id = database.update_chat_history(user_json)
        if attempt < 3:
            attempt += 1
            respond_to_chat(chat_id,attempt)
        else:
            print(f"Error: {e}")
            sys.exit(1)

    except Exception as e:
        print(f'Error: {e}')
        return
    
    response = chat_completion.choices[0].message
    tool_calls = response.tool_calls 
    database.update_chat_history(response,chat_id)

    if not tool_calls:
        print(functions.format_response(response.content))
    else:
        tools.handle_tool_calls(chat_id,tool_calls)
        
def main():
    if len(sys.argv) < 2:
        print("Usage: mewtwo <prompt>")
        sys.exit(1)
    database.initialize_user_db()
    prompt = " ".join(sys.argv[1:])
    user_json = {'role': 'user', 'content': [{"type":"text","text": prompt}]}
    chat_id = database.update_chat_history(user_json)
    respond_to_chat(chat_id)

if __name__ == "__main__":
    main()

