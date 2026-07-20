from app.agents.nrpilot import NRPilotAgent


class FakeMessage:
    content = "The api pod is running."


class FakeDeepAgent:
    def invoke(self, request: object) -> dict[str, list[FakeMessage]]:
        assert request == {"messages": [{"role": "user", "content": "Is api healthy?"}]}
        return {"messages": [FakeMessage()]}


def test_nrpilot_agent_returns_final_message() -> None:
    agent = NRPilotAgent(FakeDeepAgent())

    assert agent.ask("Is api healthy?") == "The api pod is running."
