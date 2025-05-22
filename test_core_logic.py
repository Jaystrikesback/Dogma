import unittest
import json # For checking JSON parts in mock response
from core_logic import generate_system_prompt, execute_ollama_request

class TestCoreLogic(unittest.TestCase):

    def test_generate_system_prompt_no_tools(self):
        prompt = generate_system_prompt([])
        self.assertIn("You are a helpful AI assistant.", prompt)
        # self.assertNotIn("Browser Use", prompt) # "Browser Use" is in the example JSON.
        self.assertNotIn("[TOOL_CALL: Browser Use, URL: <url_to_visit>]", prompt)
        # self.assertNotIn("SmartScrapeAI", prompt) # "SmartScrapeAI" could be in an example JSON.
        self.assertNotIn("[TOOL_CALL: SmartScrapeAI, URL: <url_for_scraping>]", prompt)
        self.assertIn("When you use a tool, you MUST report the outcome", prompt) # JSON guidance

    def test_generate_system_prompt_with_browser(self):
        prompt = generate_system_prompt(["Browser Use"])
        self.assertIn("You are a helpful AI assistant.", prompt)
        self.assertIn("Browser Use", prompt) # Check for the tool name in its instructions
        self.assertIn("[TOOL_CALL: Browser Use, URL: <url_to_visit>]", prompt)
        self.assertNotIn("[TOOL_CALL: SmartScrapeAI, URL: <url_for_scraping>]", prompt)
        self.assertIn("When you use a tool, you MUST report the outcome", prompt)

    def test_generate_system_prompt_with_smartscrape(self):
        prompt = generate_system_prompt(["SmartScrapeAI"])
        self.assertIn("You are a helpful AI assistant.", prompt)
        # self.assertNotIn("Browser Use", prompt) # "Browser Use" is in the example JSON.
        self.assertNotIn("[TOOL_CALL: Browser Use, URL: <url_to_visit>]", prompt)
        self.assertIn("SmartScrapeAI", prompt) # Check for the tool name in its instructions
        self.assertIn("[TOOL_CALL: SmartScrapeAI, URL: <url_for_scraping>]", prompt)
        self.assertIn("When you use a tool, you MUST report the outcome", prompt)

    def test_generate_system_prompt_with_all_tools(self):
        prompt = generate_system_prompt(["Browser Use", "SmartScrapeAI"])
        self.assertIn("You are a helpful AI assistant.", prompt)
        self.assertIn("Browser Use", prompt)
        self.assertIn("[TOOL_CALL: Browser Use, URL: <url_to_visit>]", prompt)
        self.assertIn("SmartScrapeAI", prompt)
        self.assertIn("[TOOL_CALL: SmartScrapeAI, URL: <url_for_scraping>]", prompt)
        self.assertIn("When you use a tool, you MUST report the outcome", prompt)

    def _extract_json_block(self, text_with_json_block):
        # Helper to extract JSON block for easier testing
        try:
            # Expecting ```json
# {...}
# ```
            start_index = text_with_json_block.index("```json\n") + len("```json\n")
            end_index = text_with_json_block.index("\n```", start_index)
            json_str = text_with_json_block[start_index:end_index]
            return json.loads(json_str)
        except (ValueError, json.JSONDecodeError) as e:
            self.fail(f"Could not extract or parse JSON block: {e}\nBlock content: {text_with_json_block}")


    def test_execute_ollama_request_mock_browser_tool(self):
        response = execute_ollama_request("http://testurl", "testmodel", "sysprompt", "userprompt", "http://target.com", ["Browser Use"])
        # Check it's the mock by looking for specific phrasing not in the JSON
        self.assertIn("Okay, I will use the Browser Use tool", response)
        json_data = self._extract_json_block(response)
        self.assertEqual(json_data["tool_used"], "Browser Use")
        self.assertEqual(json_data["tool_input"]["url"], "http://target.com")
        self.assertIn("simulated browsing to http://target.com", json_data["user_facing_answer"])

    def test_execute_ollama_request_mock_smartscrape_tool(self):
        response = execute_ollama_request("http://testurl", "testmodel", "sysprompt", "userprompt", "http://scrape.it", ["SmartScrapeAI"])
        self.assertIn("Okay, I will use the SmartScrapeAI tool", response)
        json_data = self._extract_json_block(response)
        self.assertEqual(json_data["tool_used"], "SmartScrapeAI")
        self.assertEqual(json_data["tool_input"]["url"], "http://scrape.it")
        self.assertIn("simulated scraping http://scrape.it", json_data["user_facing_answer"])
        self.assertIn("extracted_data", json_data)

    def test_execute_ollama_request_mock_no_tool(self):
        response = execute_ollama_request("http://testurl", "testmodel", "sysprompt", "userprompt", enabled_tools=[])
        self.assertIn("I'm processing your request", response) # General query mock
        json_data = self._extract_json_block(response)
        self.assertIsNone(json_data["tool_used"]) # Expecting null for tool_used
        self.assertIn("processed it without using a specific tool", json_data["user_facing_answer"])
        self.assertIn("userprompt", json_data["user_facing_answer"]) # Check if user prompt is in the answer

    def test_execute_ollama_request_mock_browser_tool_no_target_url(self):
        # Test default URL for browser tool
        response = execute_ollama_request("http://testurl", "testmodel", "sysprompt", "userprompt", enabled_tools=["Browser Use"])
        self.assertIn("Okay, I will use the Browser Use tool", response)
        json_data = self._extract_json_block(response)
        self.assertEqual(json_data["tool_used"], "Browser Use")
        self.assertEqual(json_data["tool_input"]["url"], "https://example.com/browsed") # Default URL

if __name__ == '__main__':
    unittest.main()
# Corrected assertion in test_generate_system_prompt_no_tools, _with_browser, etc.
# The prompt instructs: "When you use a tool, you MUST report the outcome of the tool's operation."
# The previous assertion "If you use a tool, try to summarize the key information" was slightly off.
# Also corrected assertions in test_execute_ollama_request_mock_... to look for more specific mock response text outside the JSON block to confirm it's the mock.
