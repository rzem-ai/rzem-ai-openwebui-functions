"""
Title: Pipe Function Template
Author: Your Name
Version: 0.1.0
License: MIT
Description: Template for creating OpenWebUI Pipe Functions
"""

from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field


class Pipe:
    """
    OpenWebUI Pipe Function Template
    
    Pipe functions allow you to process and transform data through a pipeline.
    They can be used to modify messages, add context, or integrate external services.
    """

    class Valves(BaseModel):
        """
        Valves are used to configure the pipe function.
        Add any configuration parameters your function needs here.
        """
        priority: int = Field(
            default=0,
            description="Priority of the pipe function (higher = runs earlier)"
        )
        # Add your custom configuration parameters here
        # Example:
        # api_key: str = Field(default="", description="API key for external service")

    def __init__(self):
        """Initialize the pipe function with default configuration."""
        self.type = "pipe"
        self.id = "pipe_function_template"
        self.name = "Pipe Function Template"
        self.valves = self.Valves()

    def pipes(self) -> List[Dict[str, str]]:
        """
        Define available pipes (endpoints) for this function.
        
        Returns:
            List of dictionaries containing pipe metadata
        """
        return [
            {
                "id": "pipe_function_template",
                "name": "Pipe Function Template"
            }
        ]

    async def pipe(
        self,
        body: Dict[str, Any],
        __user__: Optional[Dict[str, Any]] = None,
        __event_emitter__=None,
        __event_call__=None,
    ) -> Union[str, Dict[str, Any]]:
        """
        Main pipe function that processes the input.
        
        Args:
            body: The request body containing messages and other data
            __user__: User information (optional)
            __event_emitter__: Event emitter for streaming responses (optional)
            __event_call__: Event caller for triggering events (optional)
            
        Returns:
            Processed response (string or dict)
        """
        # Extract messages from body
        messages = body.get("messages", [])
        
        # Process the messages or add your custom logic here
        # Example: Add a system message or modify user messages
        
        # For demonstration, we'll just echo back the last message
        if messages:
            last_message = messages[-1].get("content", "")
            response = f"Processed: {last_message}"
        else:
            response = "No messages to process"
        
        # Emit events if needed (for streaming responses)
        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {"description": "Processing complete", "done": True},
                }
            )
        
        return response
