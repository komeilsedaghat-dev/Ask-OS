import platform
from openai import OpenAI
from askos import config
from askos import cache

class LLMClient:
    """
    Client interface for interacting with an OpenAI-compatible API.
    """
    def __init__(self, api_key: str = None, base_url: str = None, model_name: str = None):
        self.api_key = api_key or config.get_api_key()
        self.base_url = base_url or config.get_base_url()
        self.model_name = model_name or config.get_model_name()
        
        if not self.api_key:
            raise ValueError(
                "API key is not set. Please configure OPENAI_API_KEY in your .env file or pass it using --api-key / -k option."
            )

        # Initialize the OpenAI client with base_url and api_key
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    def generate_command(self, prompt: str) -> tuple[str, bool]:
        """
        Translates a natural language user prompt into a single clean OS command.
        Checks the cache first.
        
        Returns:
            (command, was_cached)
        """
        # Check cache
        cached_command = cache.get_cached_command(prompt, self.model_name)
        if cached_command:
            return cached_command, True

        os_name = platform.system()
        
        system_prompt = (
            f"You are a terminal command generator for {os_name}.\n"
            "Your task is to convert the user's natural language request into a single, valid terminal command.\n"
            "Respond ONLY with the raw command. Do not wrap it in markdown code blocks (like ```bash), "
            "do not explain the command, and do not add any extra commentary or formatting. "
            "Just return the raw terminal command itself."
        )

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
        )
        
        command = response.choices[0].message.content.strip()
        
        # Clean any accidental markdown code blocks
        if command.startswith("```"):
            lines = command.splitlines()
            if len(lines) >= 2:
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                command = "\n".join(lines).strip()
        
        # Save cache
        cache.set_cached_command(prompt, self.model_name, command)
                
        return command, False

    def generate_correction(self, prompt: str, failed_command: str, error_output: str) -> str:
        """
        Translates the error output of a failed command back into a corrected command.
        """
        os_name = platform.system()
        
        system_prompt = (
            f"You are an expert terminal command debugger for {os_name}.\n"
            "The user previously requested a command, which failed with an error.\n"
            "Analyze the original natural language prompt, the failed command, and its error output, "
            "then generate a single, valid, and corrected terminal command.\n"
            "Respond ONLY with the raw command. Do not wrap it in markdown code blocks, "
            "do not add explanations, and do not write anything else."
        )

        user_message = (
            f"Original Request: {prompt}\n"
            f"Failed Command: {failed_command}\n"
            f"Error Output:\n{error_output}"
        )

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.0,
        )
        
        command = response.choices[0].message.content.strip()
        
        # Clean any accidental markdown code blocks
        if command.startswith("```"):
            lines = command.splitlines()
            if len(lines) >= 2:
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                command = "\n".join(lines).strip()
                
        return command

    def explain_command(self, command: str) -> str:
        """
        Generates a plain-English explanation of the terminal command.
        """
        system_prompt = (
            "You are an expert command line tutor.\n"
            "The user will provide a terminal command. Your job is to explain what it does step-by-step in plain English.\n"
            "Keep the explanation clean, short, and bulleted. Avoid long introductions."
        )

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": command}
            ],
            temperature=0.0,
        )
        
        return response.choices[0].message.content.strip()
