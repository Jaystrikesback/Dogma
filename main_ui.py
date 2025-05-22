import tkinter as tk
from tkinter import ttk
import json
import urllib.request
import urllib.error
from core_logic import generate_system_prompt, execute_ollama_request

class DogmaAgentControlUI:
    def __init__(self, master):
        self.master = master
        master.title("Dogma Agent Control")

        # Ollama Server URL
        self.ollama_url_label = ttk.Label(master, text="Ollama Server URL:")
        self.ollama_url_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.ollama_url_entry = ttk.Entry(master, width=40) # Adjusted width
        self.ollama_url_entry.insert(0, "http://localhost:11434")
        self.ollama_url_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        self.fetch_models_button = ttk.Button(master, text="Fetch Models", command=self.fetch_ollama_models)
        self.fetch_models_button.grid(row=0, column=2, sticky="w", padx=5, pady=5)

        # Model Selection
        self.model_label = ttk.Label(master, text="Select Model:")
        self.model_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.model_combobox = ttk.Combobox(master, values=[]) # Initially empty
        self.model_combobox.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5, pady=5)

        # Target URL
        self.target_url_label = ttk.Label(master, text="Target URL (for tools):")
        self.target_url_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.target_url_entry = ttk.Entry(master, width=50)
        self.target_url_entry.grid(row=2, column=1, columnspan=2, sticky="ew", padx=5, pady=5)

        # User Prompt
        self.prompt_label = ttk.Label(master, text="User Prompt:")
        self.prompt_label.grid(row=3, column=0, sticky="nw", padx=5, pady=5)
        self.prompt_text = tk.Text(master, height=10, width=50)
        self.prompt_text.grid(row=3, column=1, columnspan=2, sticky="ew", padx=5, pady=5)

        # Enable Tools
        self.tools_label = ttk.Label(master, text="Enable Tools:")
        self.tools_label.grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.browser_use_var = tk.BooleanVar()
        self.browser_use_check = ttk.Checkbutton(master, text="Browser Use", variable=self.browser_use_var)
        self.browser_use_check.grid(row=4, column=1, sticky="w", padx=5, pady=5)
        self.smartscrape_var = tk.BooleanVar()
        self.smartscrape_check = ttk.Checkbutton(master, text="SmartScrapeAI", variable=self.smartscrape_var)
        self.smartscrape_check.grid(row=4, column=2, sticky="w", padx=5, pady=5)

        # Output Display
        self.output_label = ttk.Label(master, text="Output:")
        self.output_label.grid(row=5, column=0, sticky="nw", padx=5, pady=5)
        self.output_text_area = tk.Text(master, height=10, width=50, state=tk.DISABLED)
        # self.output_text_area.insert(tk.END, "results") # Initial message removed
        self.output_text_area.grid(row=5, column=1, columnspan=2, sticky="ew", padx=5, pady=5)


        # Submit Button
        self.submit_button = ttk.Button(master, text="Submit", command=self.handle_submit)
        self.submit_button.grid(row=6, column=1, sticky="e", padx=5, pady=10)

        # Informational Note
        self.info_label = ttk.Label(master, text="Info: Ensure Ollama is accessible (e.g., bound to 0.0.0.0 if not running on localhost).")
        self.info_label.grid(row=7, column=0, columnspan=3, sticky="w", padx=5, pady=5)

        # Configure column weights for resizing
        master.columnconfigure(1, weight=1)
        # master.columnconfigure(2, weight=1) # Column 2 no longer needs to take all remaining space

    def fetch_ollama_models(self):
        ollama_url = self.ollama_url_entry.get().strip()
        if not ollama_url:
            self.update_output_area("Error: Ollama Server URL cannot be empty.")
            return

        api_url = f"{ollama_url}/api/tags"

        try:
            self.update_output_area("Fetching models...") # Inform user
            with urllib.request.urlopen(api_url, timeout=5) as response:
                if response.status == 200:
                    data = json.load(response)
                    if "models" in data and isinstance(data["models"], list):
                        model_names = [model.get("name") for model in data["models"] if model.get("name")]
                        if model_names:
                            self.model_combobox['values'] = model_names
                            self.model_combobox.set('') # Clear selection or set to a default
                            self.update_output_area(f"Successfully fetched {len(model_names)} models.")
                        else:
                            self.model_combobox['values'] = []
                            self.model_combobox.set('')
                            self.update_output_area("No models found at the server.")
                    else:
                        self.model_combobox['values'] = []
                        self.model_combobox.set('')
                        self.update_output_area("Error: Unexpected JSON structure from Ollama API.")
                else:
                    self.update_output_area(f"Error: Failed to fetch models. Status code: {response.status}")
        except urllib.error.URLError as e:
            self.update_output_area(f"Error fetching models: {e.reason}")
        except json.JSONDecodeError:
            self.update_output_area("Error: Could not parse JSON response from Ollama API.")
        except Exception as e: # Catch any other unexpected errors
            self.update_output_area(f"An unexpected error occurred: {e}")

    def update_output_area(self, message):
        self.output_text_area.config(state=tk.NORMAL)
        self.output_text_area.delete('1.0', tk.END)
        self.output_text_area.insert(tk.END, message)
        self.output_text_area.config(state=tk.DISABLED)

    def handle_submit(self):
        ollama_url = self.ollama_url_entry.get().strip()
        selected_model = self.model_combobox.get()
        target_url = self.target_url_entry.get().strip()
        user_prompt = self.prompt_text.get("1.0", tk.END).strip()

        enabled_tools = []
        if self.browser_use_var.get():
            enabled_tools.append("Browser Use")
        if self.smartscrape_var.get():
            enabled_tools.append("SmartScrapeAI")

        print(f"Ollama URL: {ollama_url}")
        print(f"Selected Model: {selected_model}")
        print(f"Target URL: {target_url}")
        print(f"User Prompt: {user_prompt}")
        print(f"Enabled Tools: {enabled_tools}")

        # Generate System Prompt
        system_prompt = generate_system_prompt(enabled_tools)

        # Call the placeholder backend function (execute_ollama_request)
        mock_response = execute_ollama_request(
            ollama_url=ollama_url,
            model_name=selected_model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            target_url=target_url,
            enabled_tools=enabled_tools
        )

        # Process and display this mock response
        self.process_and_display_output(mock_response)

    def process_and_display_output(self, raw_model_output: str):
        raw_model_output = raw_model_output.strip() if raw_model_output else ""

        if not raw_model_output:
            self.update_output_area("results")
            return

        # Try to find the JSON block as specified in core_logic.py
        # ```json
        # { ... }
        # ```
        json_block_start_marker = "```json\n"
        json_block_end_marker = "\n```"
        
        start_index = raw_model_output.find(json_block_start_marker)
        
        if start_index != -1:
            # Adjust start_index to be after the marker
            actual_json_start = start_index + len(json_block_start_marker)
            # Find the end of the JSON block
            end_index = raw_model_output.find(json_block_end_marker, actual_json_start)
            
            if end_index != -1:
                json_string = raw_model_output[actual_json_start:end_index].strip()
                try:
                    parsed_json = json.loads(json_string)
                    if isinstance(parsed_json, dict) and "user_facing_answer" in parsed_json:
                        self.update_output_area(parsed_json["user_facing_answer"])
                        return # Successfully displayed the specific answer
                    else:
                        # JSON found and parsed, but no 'user_facing_answer' or not a dict
                        self.update_output_area(f"Parsed JSON, but 'user_facing_answer' key missing or invalid structure:\n{json_string}\n\nFull output:\n{raw_model_output}")
                        return
                except json.JSONDecodeError:
                    # JSON block markers found, but content is not valid JSON
                    self.update_output_area(f"Found JSON block markers, but failed to parse JSON:\n{json_string}\n\nFull output:\n{raw_model_output}")
                    return

        # If no JSON block, or parsing failed and we decided to show full output
        self.update_output_area(raw_model_output)


if __name__ == '__main__':
    root = tk.Tk()
    gui = DogmaAgentControlUI(root)
    root.mainloop()
