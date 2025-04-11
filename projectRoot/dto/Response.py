class Response:
    def __init__(self, answer, action, info, memory, modifiedPrompt):
        """
        answer: will contain the actual string that the user will read
        action: will contain the token that is used to navigate the agent behaviour
        info: will be used to pass additional information between different phases of the agent
        memory: will be used to store the conversation history
        modifiedPrompt: will be used to store the eventually modified prompt that will be used to generate the answer

        If answer is blank this mean tah the produced output will be routed toward another pahse of the agent
        """
        self.answer = answer
        self.action = action
        self.info = info
        self.memory = memory
        self.modifiedPrompt = modifiedPrompt