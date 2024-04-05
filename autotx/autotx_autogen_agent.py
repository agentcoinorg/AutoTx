import autogen

class AutoTxAutogenAgent():
    autogen_agent: autogen.Agent
    tools: list[str]

    def __init__(self, autogen_agent: autogen.Agent, tools: list[str]):
        self.autogen_agent = autogen_agent
        self.tools = tools