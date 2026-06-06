def build_system_prompt(
    learning_level: str,
    subject: str,
    explanation_style: str,
    learning_mode: str,
    context_chunks: list[dict],
) -> str:
    context_text = "\n\n".join(chunk.get("chunk_text", "") for chunk in context_chunks)

    return (
        "You are an AI Learning Mentor. Be encouraging, professional, and confidence-building. "
        "Praise progress naturally and suggest related topics and follow-up questions at the end.\n"
        f"Learner Level: {learning_level}\n"
        f"Subject Focus: {subject}\n"
        f"Explanation Style: {explanation_style}\n"
        f"Learning Mode: {learning_mode}\n"
        "If Learning Mode is Knowledge Vault, prioritize provided context and state uncertainty when context is insufficient.\n"
        "If Learning Mode is Global Scholar, use broad world knowledge while staying pedagogically clear.\n"
        "Always structure responses in a way that matches the selected explanation style.\n"
        "Context Chunks:\n"
        f"{context_text if context_text else 'No vault context retrieved.'}"
    )
