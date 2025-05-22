# Preferred JSON output structure for tool usage:
# {
#   "tool_used": "Browser Use" | "SmartScrapeAI",
#   "tool_input": {"url": "<url_string>"}, // Or other relevant inputs for SmartScrapeAI
#   "summary": "<A brief summary of what the tool did or found, or an error message if it failed>",
#   "extracted_data": { ... }, // Optional, primarily for SmartScrapeAI if it extracts structured data
#   "user_facing_answer": "<The part of your response that should be directly shown to the user, incorporating tool findings or explaining why a tool could not be used>"
# }

def generate_system_prompt(enabled_tools: list[str]) -> str:
    """
    Constructs a system prompt for the LLM, instructing it on tool usage and output format.
    """
    prompt_parts = [
        "You are a helpful AI assistant. Your goal is to answer the user's request accurately and concisely."
        "You have access to the following tools to help gather information or interact with web pages:"
    ]

    if not enabled_tools:
        prompt_parts.append("\nNo tools are currently enabled. You will have to answer based on your existing knowledge.")
    else:
        prompt_parts.append("\nTo use a tool, you MUST issue a command in the specified format in your response. "
                            "Do not attempt to use a tool if the user's request does not require it or if a previous tool use failed for that target.")
        prompt_parts.append("Tool usage instructions:")

    tool_descriptions = {
        "Browser Use": (
            "  - **Browser Use**: Accesses a given URL and returns its textual content. "
            "Useful for fetching information from web pages. "
            "To use, issue a command in the format: `[TOOL_CALL: Browser Use, URL: <url_to_visit>]`"
        ),
        "SmartScrapeAI": (
            "  - **SmartScrapeAI**: Extracts structured information from a webpage based on a user's query. "
            "Use this when the user asks for specific data points from a URL. "
            "To use, issue a command in the format: `[TOOL_CALL: SmartScrapeAI, URL: <url_for_scraping>]`"
        )
    }

    for tool_name in enabled_tools:
        if tool_name in tool_descriptions:
            prompt_parts.append(tool_descriptions[tool_name])

    prompt_parts.append(
        "\nWhen you use a tool, you MUST report the outcome of the tool's operation. "
        "Critically, if a tool call is made, you should summarize the key information from the tool's operation "
        "in a JSON block like this, followed by your conversational response incorporating this information:"
        "\n```json\n"
        "{\n"
        '  "tool_used": "<tool_name>",\n'
        '  "tool_input": {"url": "<url_used_with_tool>"},\n' # Assuming URL is common input for now
        '  "summary": "<brief_summary_of_tool_action_or_data_found>",\n'
        '  "user_facing_answer": "<your_response_to_user_incorporating_this_summary>"\n'
        "}\n"
        "```\n"
        "For example, if you used 'Browser Use' on 'example.com' and found 'Data X', your response might include:\n"
        "```json\n"
        "{\n"
        '  "tool_used": "Browser Use",\n'
        '  "tool_input": {"url": "https://example.com"},\n'
        '  "summary": "Successfully fetched content from example.com. Found relevant information: Data X.",\n'
        '  "user_facing_answer": "I found \'Data X\' on example.com. This information helps answer your question by..."\n'
        "}\n"
        "```\n"
        "If a tool fails, use the 'summary' field to explain the failure (e.g., 'URL was inaccessible', 'Content not found').\n"
        "The 'user_facing_answer' in the JSON should be the complete, user-ready part of your response that integrates the tool's findings or explains the situation. "
        "Your entire response will be a combination of your thoughts, the JSON block (if a tool is used), and then your final conversational answer which should align with the 'user_facing_answer' in the JSON."
        "\nIf the user's request does not require any tool, or if you are providing a general answer, do not include the JSON block."
        "\nAlways prioritize accuracy and relevance in your responses."
    )
    return "\n\n".join(prompt_parts)

if __name__ == '__main__':
    # Example usage:
    print("---- Example 1: No tools ----")
    print(generate_system_prompt([]))
    print("\n---- Example 2: Browser Use only ----")
    print(generate_system_prompt(["Browser Use"]))
    print("\n---- Example 3: Both tools ----")
    print(generate_system_prompt(["Browser Use", "SmartScrapeAI"]))
    print("\n---- Example 4: Unknown tool (should be ignored by prompt) ----")
    print(generate_system_prompt(["Browser Use", "ImaginaryTool"]))

def execute_ollama_request(ollama_url: str, model_name: str, system_prompt: str, user_prompt: str, target_url: str = None, enabled_tools: list[str] = None) -> str:
    """
    Simulates a request to an Ollama-compatible LLM.
    In a real implementation, this would involve an HTTP request.
    For now, it returns a hardcoded response based on enabled tools.
    """
    print(f"\nExecuting Ollama request (mock):")
    print(f"  Ollama URL: {ollama_url}")
    print(f"  Model: {model_name}")
    print(f"  System Prompt (first 100 chars): {system_prompt[:100]}...")
    print(f"  User Prompt: {user_prompt}")
    print(f"  Target URL: {target_url}")
    print(f"  Enabled Tools: {enabled_tools}")

    mock_json_output = ""
    tool_used_in_mock = None

    if enabled_tools: # Check if enabled_tools is not None and not empty
        if "Browser Use" in enabled_tools:
            actual_target_url = target_url if target_url else "https://example.com/browsed"
            mock_json_output = f'''```json
{{
  "tool_used": "Browser Use",
  "tool_input": {{"url": "{actual_target_url}"}},
  "summary": "Simulated fetching content from {actual_target_url}.",
  "user_facing_answer": "I have simulated browsing to {actual_target_url}. The page seems to contain general information and examples."
}}
```'''
            tool_used_in_mock = "Browser Use"
        elif "SmartScrapeAI" in enabled_tools:
            actual_target_url = target_url if target_url else "https://example.com/scraped"
            mock_json_output = f'''```json
{{
  "tool_used": "SmartScrapeAI",
  "tool_input": {{"url": "{actual_target_url}"}},
  "summary": "Simulated scraping data from {actual_target_url}.",
  "extracted_data": {{"info": "some scraped data", "value": 123}},
  "user_facing_answer": "I have simulated scraping {actual_target_url} and found some interesting data points."
}}
```'''
            tool_used_in_mock = "SmartScrapeAI"

    if not tool_used_in_mock: # Default mock if no specific tool enabled or for general queries
        # Ensure user_prompt is escaped for JSON if it's directly embedded, though here it's only in a comment
        escaped_user_prompt_summary = user_prompt[:50].replace('"', '\\"')
        mock_json_output = f'''```json
{{
  "tool_used": null,
  "tool_input": null,
  "summary": "No specific tool was invoked for the query or selected tool was not mockable. Processed general query.",
  "user_facing_answer": "This is a simulated response to your query: '{escaped_user_prompt_summary}...' I have processed it without using a specific tool for this mock."
}}
```'''

    # Simulate a more complete LLM response structure
    if tool_used_in_mock:
        response_text = (
            f"Okay, I will use the {tool_used_in_mock} tool for your request regarding '{user_prompt[:30]}...'.\n"
            f"{mock_json_output}\n"
            f"The simulation for {tool_used_in_mock} is now complete. Let me know if you need further assistance."
        )
    else:
        response_text = (
            f"I'm processing your request: '{user_prompt[:30]}...'.\n"
            f"{mock_json_output}\n"
            f"This concludes my simulated response based on the general query."
        )
    
    print(f"  Mock Response (first 100 chars): {response_text[:100]}...")
    return response_text
