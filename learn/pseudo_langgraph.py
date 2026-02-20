from typing import TypedDict

class State(TypedDict):
    query: str
    category: str
    answer: str
    

def router_node(state: State):
    if "RTX" in state['query'] or "5080" in state['query']:
        state['category'] = 'PC_TECH'
        return {'category': 'PC_TECH'}
    
    
def pc_agent_node(state: State):
    state['answer'] = "Check your OpenRGB settings or fan curves!"


if __name__ == '__main__':
    
    state: State = {
    "query": "My RTX 5080 is running hot",
    "category": None,
    "answer": None
    }
    
    update = router_node(state=state)
    
    if state["category"] == "PC_TECH":
        pc_agent_node(state)
        
    print(state['answer'])

    