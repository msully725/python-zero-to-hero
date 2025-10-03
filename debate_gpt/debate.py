from dataclasses import dataclass, field
import chat_completion_api as api

@dataclass
class ChatMessage:
    content: str
    role: str = "user"

    def to_dict(self):
        return { "role": self.role, "content": self.content }

@dataclass
class ChatThread:
    messages: list[ChatMessage] = field(default_factory=list)

    def to_request(self):
        return [message.__dict__ for message in self.messages]

class Debater:
    def __init__(self, name: str, position: str, initial_prompt: str):
        self.name = name
        self.position = position
        self.thread = ChatThread()
        self.thread.messages = [ChatMessage(initial_prompt)]

    def receive_opponent_response(self, opponent_response: str):
        """Receive and incorporate the opponent's response into our thread."""
        opponent_message = ChatMessage(f"Your opponent has said: {opponent_response}", "user")
        self.thread.messages.append(opponent_message)

    def generate_response(self) -> str:
        """Generate our response using the current thread state."""
        response = api.send_chat_completion_request(self.thread.to_request())
        if response and 'choices' in response:
            content = response['choices'][0]['message']['content']
            # Add our response to our own thread for context
            self.thread.messages.append(ChatMessage(content, "assistant"))
            return content
        return ""

class Moderator:
    def __init__(self, debater1: Debater, debater2: Debater):
        self.debater1 = debater1
        self.debater2 = debater2

    def conduct_single_round(self):
        """Conduct a single round of debate: D1 speaks, D2 responds."""
        print("=== DEBATE: Chevy vs Ford ===")
        print()

        # Debater 1's opening statement
        print(f"{self.debater1.name} ({self.debater1.position}):")
        d1_response = self.debater1.generate_response()
        print(d1_response)
        print()

        # Give D1's response to D2 and get D2's response
        self.debater2.receive_opponent_response(d1_response)

        print(f"{self.debater2.name} ({self.debater2.position}):")
        d2_response = self.debater2.generate_response()
        print(d2_response)
        print()

        print("Single round debate completed!")

chevy_debater = Debater(
    name="Debater One",
    position="Chevy",
    initial_prompt="You are in a debate. You will defend your position ardently. Your responses will be at most three sentences. The debate will end when you decide the other person's arguments have persuaded you to change your position. The debate may not end with such an outcome and may require a debate moderator to declare the debate over. The topic is Chevy vs Ford. Your position is Chevy is better than Ford. Start the debate and make your claim on your position."
)

ford_debater = Debater(
    name="Debater Two",
    position="Ford",
    initial_prompt="You are in a debate. You will defend your position ardently. Your responses will be at most three sentences. The debate will end when you decide the other person's arguments have persuaded you to change your position. The debate may not end with such an outcome and may require a debate moderator to declare the debate over. The topic is Chevy vs Ford. Your position is Ford is better than Chevy."
)

debate_moderator = Moderator(chevy_debater, ford_debater)
debate_moderator.conduct_single_round()