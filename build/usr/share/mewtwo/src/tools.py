from src import database 
from src import documentReader
from src import run_commands
from RAG import rag
import mewtwo
import json 
available_tools = {
    'run_commands': run_commands.run_commands,
    'documentReader': documentReader.documentReader,
    'search_documentation': rag.rag
}
tools = [
    documentReader.spec,
    run_commands.spec,
    rag.spec,
]

def handle_tool_calls(chat_id, tool_calls):
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_to_call = available_tools.get(function_name)
        function_args = json.loads(tool_call.function.arguments)

        if function_name == "documentReader":
            try:
                document_text = function_to_call(
                    filepath = function_args.get('filepath')
                )
                database.update_chat_history({
                    'role':'tool',
                    'content': document_text,
                    'tool_call_id': tool_call.id
                },chat_id)
            except Exception as e:
                database.update_chat_history({
                    'role':'tool',
                    'content': f'There was an error retrieving the contents from the document: {e}',
                    'tool_call_id': tool_call.id
                },chat_id)

        if function_name == 'run_commands':
            try:
                function_response = function_to_call(
                    commands = function_args.get("commands"),
                    verbose = function_args.get("verbose")
                )
                database.update_chat_history({
                    'role':'tool',
                    'content': f'''
Result of `run_commands` executed by the assistant:
```
{function_response}
```
''','tool_call_id': tool_call.id
                }, chat_id)

            except Exception as e:
                database.update_chat_history({
                    'role':'tool',
                    'content':f'There was an error: \n ```\n{e}\n```',
                    'tool_call_id':tool_call.id
                    },chat_id)
                
        if function_name == 'search_documentation':
            if function_args.get('filepath', None) is not None:
                where = {'filepath': function_args.get('filepath')}
            else:
                where = None
            results = function_to_call(
                query_text = function_args.get('query_text'), 
                top_k=10, 
                where = where
                )
            database.update_chat_history({
                'role': 'tool',
                'content': f'''
Search results:
{results}
''','tool_call_id': tool_call.id
            }, chat_id)
    mewtwo.respond_to_chat(chat_id)