import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

AVAILABLE_MODELS = {
    "1": ("deepseek/deepseek-r1", "DeepSeek R1"),
    "2": ("openai/gpt-4o-mini","GPT-4o Mini"),
}


class ChatAgent:
    def __init__(
        self,
        model: str,
        system_prompt: str = "You are a helpful assistant.",
        max_turns: int = 10,
        compact_mode: str = "summary",
    ):
        self.model = model
        self.system_prompt = system_prompt
        self.max_turns = max_turns
        self.compact_mode = compact_mode

        self.history = []

        api_key = os.getenv("OPENROUTER_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY not found in .env file"
            )

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ["OPENROUTER_API_KEY"],
        )

    def _build_messages(self):
        return [
            {"role": "system", "content": self.system_prompt}
        ] + self.history

    def _over_limit(self):
        return len(self.history) > self.max_turns * 2

    def _compact_drop(self):
        if len(self.history) >= 2:
            self.history = self.history[2:]
            print("\n[system] Oldest turn dropped.\n")

    def _compact_summarise(self):
        print("\n[system] Summarising history...\n")

        summary_prompt = (
            "Summarise this conversation in 3-5 concise sentences:\n\n"
            + "\n".join(
                f"{m['role'].upper()}: {m['content']}"
                for m in self.history
            )
        )

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": summary_prompt}
                ],
                max_tokens=300,
            )

            summary_text = (
                resp.choices[0].message.content.strip()
            )

            self.history = [
                {
                    "role": "assistant",
                    "content": (
                        f"[Earlier conversation summary]: "
                        f"{summary_text}"
                    ),
                }
            ]

        except Exception as e:
            print(f"[system] Summary failed: {e}")

    def compact(self):
        if not self.history:
            print("[system] Nothing to compact.\n")
            return

        self._compact_summarise()

    def _maybe_compact(self):
        if self._over_limit():
            if self.compact_mode == "summary":
                self._compact_summarise()
            else:
                self._compact_drop()

    def call_model(self, user_message: str):
        self.history.append(
            {"role": "user", "content": user_message}
        )

        self._maybe_compact()

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self._build_messages(),
            )

            reply = (
                response.choices[0]
                .message.content.strip()
            )

            self.history.append(
                {
                    "role": "assistant",
                    "content": reply,
                }
            )

            self.last_usage = response.usage

            return reply

        except Exception as e:
            error_msg = str(e)

            if "404" in error_msg:
                return (
                    "\nModel not available on OpenRouter.\n"
                    "Choose another model.\n"
                )

            if "401" in error_msg:
                return (
                    "\nInvalid API key.\n"
                    "Check OPENROUTER_API_KEY.\n"
                )

            return f"\nAPI Error:\n{error_msg}\n"

    def reset(self):
        self.history = []
        print("[system] History cleared.\n")

    def show_tokens(self):
        if not hasattr(self, "last_usage"):
            print("[system] No API call made yet.\n")
            return

        u = self.last_usage

        print(
            f"[tokens] "
            f"prompt={u.prompt_tokens} "
            f"completion={u.completion_tokens} "
            f"total={u.total_tokens}\n"
        )


def choose_model():
    print("=" * 50)
    print("Select a model")
    print("=" * 50)

    for key, (_, label) in AVAILABLE_MODELS.items():
        print(f"{key}. {label}")

    print("=" * 50)

    while True:
        choice = input(
            "Enter number (default 1): "
        ).strip() or "1"

        if choice in AVAILABLE_MODELS:
            model_id, label = AVAILABLE_MODELS[choice]
            print(f"\nUsing: {label}\n")
            return model_id

        print("Invalid choice.")


def run_chatbot():
    print("run_chatbot started")
    model = choose_model()

    agent = ChatAgent(
        model=model,
        system_prompt="You are a helpful assistant.",
        max_turns=6,
        compact_mode="summary",
    )

    print(
        "Commands: exit | quit | /reset | "
        "/tokens | /compact\n"
    )

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        if user_input.lower() == "/reset":
            agent.reset()
            continue

        if user_input.lower() == "/tokens":
            agent.show_tokens()
            continue

        if user_input.lower() == "/compact":
            agent.compact()
            continue

        reply = agent.call_model(user_input)

        print(f"\nAssistant: {reply}\n")

print("reached end of file")
if __name__ == "__main__":
    run_chatbot()