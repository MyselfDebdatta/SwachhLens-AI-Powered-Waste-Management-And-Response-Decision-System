from typing import Dict, Any


def generate_dummy_reply(incoming: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a generic dummy assistant reply.

    This function intentionally returns a safe, generic response used by the
    Phase 1 MVP. It must not reference internal endpoints or project internals.
    """
    session_id = incoming.get("session_id")
    reply = {
        "session_id": session_id,
        "role": "assistant",
        "user_id": "system",
        "message": (
            "Hello! I'm SwachhLens AI Assistant. I can help you with:\n\n"
            "• Smart bin monitoring\n"
            "• Route optimization\n"
            "• Waste collection status\n"
            "• Maintenance requests\n"
            "• Analytics\n"
            "• AI predictions\n\n"
            "This is currently a Phase 2 placeholder response. LLM capabilities will be added in Phase 3."
        ),
        "context": incoming.get("context", {})
    }
    return reply
