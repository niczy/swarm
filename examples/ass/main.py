from swarm import Swarm, Agent
from swarm.util import function_to_json
from dotenv import load_dotenv
import json

load_dotenv()

def search_for_tool(query: str) -> dict | None:
    '''search for tool is used search among the tool box for the best tool
    to accomplish the request described in the query'''
    print("search for tool called: " + query)
    if 'lodgify' in query or 'booking' in query:
        return function_to_json(query_lodgify)
    if 'email' in query:
        return function_to_json(send_email)
    if 'current date' in query:
        return function_to_json(get_current_date)
    if 'math' in query:
        return function_to_json(math_tool)
    return None


def get_current_date()-> str:
    '''get_current_date returns current date in the real world'''
    return "2024-08-01"

def send_email(title: str, content: str, recipient: str) -> bool:
    '''send_email is used for sending an email to specified recipient'''
    print('email ' + title + " sent")
    return True

def query_lodgify(start_date: str, end_date: str) -> dict:
    '''query_lodgify is used for getting bookings between specified start_date and end_date.
       The returned json will contain  an json array of 'items', which contains the list of bookings.
    '''
    return {"items": [{"guest name": "nic", "check in date": "2024-08-01", "checkout date": "2024-10-01"}]} 
 
def math_tool(query: str) -> str:
    '''Math tool can exeucte simple and complex math caculations, for examples:
    query: 1+2, response: 3
    query: 2^3+1, response: 9
    '''
    return str(eval(query))

# Create a dictionary mapping function names to their corresponding functions
function_map = {
    "get_current_date": get_current_date,
    "send_email": send_email,
    "query_lodgify": query_lodgify,
    "math_tool": math_tool
}

def new_execution_agent(functions: list[dict]) -> Agent:
    return Agent(
        name="Executor",
        instructions='''You are a helpfull agent who can accomplish things on behalf of the user.
        The user has provided their request, the other AI agent has planed the detail of the steps to
        execute the request and researched what tools to use for each step. Please carefully read the
        previous chat history, and execute the plan as described by calling each tools.
        ''',
        functions = [function_map[f['function']['name']] for f in functions]
    )

PlannerAgent = Agent(
    name="Planner Agent",
    instructions='''You are a helpfull agent who can plan execution behalf of the user.

    When presented a request from the user. You will first layout the plan to execute the request
    step by step and call search_for_tool to research what tools to use for each step. 
    e.g. You will call search_for_tool('Any tool for doing math?') to find a tool that can do math.
    or you call call search_for_tool('Tool for querying booking details from lodgify?') for 
    getting booking details from lodgify.com.

    You only need to specify the execution steps and invoke the search_for_tool to get individual tool
    for each step. However, you DO NOT need to invoke the individual tool identified by search_for_tool.

    When search_for_tool returns None for one of your planed step, you will first try
    different queries to see if search_for_tool will return any tool or  you will revise the plan to avoid
    depend on such tool to accomplish the task. If you have exausted all possible tool combinations, but still
    can't fullfil user's request, you will response "sorry, I can't help with that " and explain why.
    ''',
    functions=[search_for_tool],
)

client = Swarm()

request =  [{"role": "user", "content": "Get all bookings from lodgify and email them to blabal@gmail.com"}]
response = client.run(
    agent=PlannerAgent,
    messages= request,
)

# request = [{"role": "user", "content": "what's 3+5"}]
# response = client.run(
#     agent=PlannerAgent,
#     messages=request,
# )

print("Planning")

functions: list[dict]  = []
for m in response.messages:
    # print("\n----")
    # print(m)
    if m['role'] == 'tool':
        content = m['content']
        # print(f"Type of content: {type(content)}")
        try:
            content_dict = json.loads(content)
            functions.append(content_dict)
        except json.JSONDecodeError:
            print(f"Error: Unable to parse content as JSON: {content}")
        except AttributeError:
            print(f"Error: 'functions' is not a list. Current type: {type(functions)}")
        except TypeError as e:
            print(f"TypeError occurred: {e}")
            print(f"Current type of 'functions': {type(functions)}")
            print(f"Content of 'functions': {functions}")


print("Execution functions:")
for function in functions:
    print(function)

execution_agent = new_execution_agent(functions)

response = client.run(
    agent=execution_agent,
    messages= request + response.messages 
)


for m in response.messages:
    print("\n----")
    print(m)