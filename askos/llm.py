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
        Translates a natural language user prompt into a clean OS command or sequence of chained commands.
        Checks the cache first.
        
        Returns:
            (command, was_cached)
        """
        # Check cache
        cached_command = cache.get_cached_command(prompt, self.model_name)
        if cached_command:
            return cached_command, True

        os_name = platform.system()
        from askos.utils import collect_environment_context
        env_context = collect_environment_context()
        
        system_prompt = (
            f"You are a terminal command generator for {os_name}.\n"
            "Your task is to convert the user's natural language request into a valid terminal command or a sequence of chained/combined commands (using operators like &&, ;, or newlines as appropriate for the shell) to achieve the goal.\n"
            "If the request requires multiple steps or commands, chain them appropriately (prefer using logical chaining operators like && or ;, or system-appropriate ways rather than multiline script blocks, to make it easier to view and edit in-place).\n"
            "Respond ONLY with the raw command(s). Do not wrap it in markdown code blocks (like ```bash), "
            "do not explain the command, and do not add any extra commentary or formatting. "
            "Just return the raw command execution block itself.\n\n"
            "Generate your command according to this system context:\n"
            f"{env_context}"
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
        Translates the error output of a failed command back into a corrected command or sequence of commands.
        """
        os_name = platform.system()
        from askos.utils import collect_environment_context
        env_context = collect_environment_context()
        
        system_prompt = (
            f"You are an expert terminal command debugger for {os_name}.\n"
            "The user previously requested a command, which failed with an error.\n"
            "Analyze the original natural language prompt, the failed command, and its error output, "
            "then generate a valid, corrected terminal command or sequence of commands.\n"
            "If multiple steps or commands are needed, chain them appropriately using operators like && or ; (prefer single-line chaining where possible).\n"
            "Respond ONLY with the raw command(s). Do not wrap it in markdown code blocks, "
            "do not add explanations, and do not write anything else.\n\n"
            "Generate your corrected command according to this system context:\n"
            f"{env_context}"
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

    def explain_command_stream(self, command: str):
        """
        Streams a plain-English explanation of the terminal command.
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
            stream=True,
        )
        
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                yield content
