from dataclasses import dataclass, field
import chat_completion_api as api
import json

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

        self._log_initialization(initial_prompt[:150] + "...")

    def _log_initialization(self, prompt: str):
        """Log debater initialization."""
        print(f"🤖 Initialized {self.name} ({self.position}) with prompt:")
        print(f"'{prompt}'")
        print()

    def _log_thread_state(self, title: str):
        """Log current thread state."""
        print(f"\n🔍 {title} - {self.name} ({self.position}) Thread:")
        print("=" * 60)
        for i, msg in enumerate(self.thread.messages, 1):
            print(f"[{i}] {msg.role.upper()}: {msg.content[:100]}{'...' if len(msg.content) > 100 else ''}")
        print("=" * 60)

    def _log_receiving_opponent(self, response: str):
        """Log when receiving opponent response."""
        print(f"\n📨 {self.name} receiving opponent response...")
        print(f"Opponent said: {response[:200]}{'...' if len(response) > 200 else ''}")

    def _log_api_request(self, request: dict):
        """Log API request data."""
        print(f"\n🚀 API REQUEST for {self.name}:")
        print(json.dumps(request, indent=2))

    def _log_api_response(self, response: dict):
        """Log raw API response."""
        print(f"\n📥 RAW API RESPONSE for {self.name}:")
        print(json.dumps(response, indent=2))

    def _log_generated_response(self, content: str):
        """Log generated response content."""
        print(f"\n💬 GENERATED RESPONSE for {self.name}:")
        print(f"'{content}'")

    def _log_error(self, message: str):
        """Log error messages."""
        print(f"\n❌ ERROR: {message}")

    def receive_opponent_response(self, opponent_response: str):
        """Receive and incorporate the opponent's response into our thread."""
        self._log_receiving_opponent(opponent_response)

        opponent_message = ChatMessage(f"Your opponent has said: {opponent_response}", "user")
        self.thread.messages.append(opponent_message)

        self._log_thread_state("AFTER RECEIVING OPPONENT RESPONSE")

    def generate_response(self) -> str:
        """Generate our response using the current thread state."""
        self._log_thread_state("BEFORE GENERATING RESPONSE")

        request_data = self.thread.to_request()
        self._log_api_request(request_data)

        response = api.send_chat_completion_request(request_data)
        self._log_api_response(response)

        if response and 'choices' in response:
            content = response['choices'][0]['message']['content']
            self._log_generated_response(content)

            # Add our response to our own thread for context
            self.thread.messages.append(ChatMessage(content, "assistant"))

            self._log_thread_state("AFTER ADDING OWN RESPONSE")
            return content

        self._log_error(f"No valid response from API for {self.name}")
        return ""

class Moderator:
    def __init__(self, debater1: Debater, debater2: Debater):
        self.debater1 = debater1
        self.debater2 = debater2

    def _log_debate_start(self):
        """Log debate initialization."""
        print("🎭 === DEBATE: Chevy vs Ford ===")
        print("📋 Single Round Format: D1 Opening → D2 Response")
        print("=" * 80)
        print()

    def _log_initial_states(self):
        """Log initial thread states header."""
        print("📋 INITIAL THREAD STATES:")

    def _log_round_section(self, round_num: int, title: str):
        """Log round section header."""
        print(f"\n{'='*80}")
        print(f"🎤 ROUND {round_num}: {title}")
        print("="*80)

    def _log_debater_turn(self, debater, action: str):
        """Log debater turn information."""
        print(f"\n👤 {debater.name} ({debater.position}) {action}...")

    def _log_final_output(self, debater, output_type: str, content: str):
        """Log final output for a debater."""
        print(f"\n🎯 FINAL OUTPUT - {debater.name}'s {output_type}:")
        print(f"'{content}'")
        print()

    def _log_debate_end(self):
        """Log debate completion."""
        print("\n" + "="*80)
        print("🏁 DEBATE ROUND COMPLETED")
        print("="*80)
        print("📋 FINAL THREAD STATES:")

    def conduct_single_round(self):
        """Conduct a single round of debate: D1 speaks, D2 responds."""
        self._log_debate_start()
        self._log_initial_states()

        # Initial thread states - use debater's own logging
        self.debater1._log_thread_state("INITIAL")
        self.debater2._log_thread_state("INITIAL")

        self._log_round_section(1, "DEBATER 1'S OPENING STATEMENT")

        # Debater 1's opening statement
        self._log_debater_turn(self.debater1, "begins the debate")
        d1_response = self.debater1.generate_response()

        self._log_final_output(self.debater1, "Opening Statement", d1_response)

        self._log_round_section(1, "DEBATER 2'S RESPONSE")

        # Give D1's response to D2 and get D2's response
        self._log_debater_turn(self.debater2, "receives opponent statement and responds")
        self.debater2.receive_opponent_response(d1_response)

        d2_response = self.debater2.generate_response()

        self._log_final_output(self.debater2, "Response", d2_response)

        self._log_debate_end()

        # Final thread states - use debater's own logging
        self.debater1._log_thread_state("FINAL")
        self.debater2._log_thread_state("FINAL")

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