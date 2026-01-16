"""
Title: Filter Function Template
Author: Your Name
Version: 0.1.0
License: MIT
Description: Template for creating OpenWebUI Filter Functions
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class Filter:
    """
    OpenWebUI Filter Function Template
    
    Filter functions intercept and modify messages before and after they are processed.
    They can be used for content moderation, logging, adding metadata, or transforming requests/responses.
    """

    class Valves(BaseModel):
        """
        Valves are used to configure the filter function.
        Add any configuration parameters your function needs here.
        """
        priority: int = Field(
            default=0,
            description="Priority of the filter function (higher = runs earlier)"
        )
        # Add your custom configuration parameters here
        # Example:
        # enabled: bool = Field(default=True, description="Enable or disable the filter")

    class UserValves(BaseModel):
        """
        User-specific valves that can be configured per user.
        These settings override the global Valves for specific users.
        """
        pass
        # Add user-specific configuration parameters here
        # Example:
        # user_preference: str = Field(default="default", description="User preference")

    def __init__(self):
        """Initialize the filter function with default configuration."""
        self.type = "filter"
        self.id = "filter_function_template"
        self.name = "Filter Function Template"
        self.valves = self.Valves()

    def inlet(
        self,
        body: Dict[str, Any],
        __user__: Optional[Dict[str, Any]] = None,
        __event_emitter__=None,
        __event_call__=None,
    ) -> Dict[str, Any]:
        """
        Inlet filter - processes messages before they are sent to the model.
        
        This is called when a user sends a message, before it reaches the LLM.
        Use this to modify the request, add context, or validate input.
        
        Args:
            body: The request body containing messages and other data
            __user__: User information (optional)
            __event_emitter__: Event emitter for streaming responses (optional)
            __event_call__: Event caller for triggering events (optional)
            
        Returns:
            Modified request body
        """
        print(f"Inlet filter called for user: {__user__.get('name', 'Unknown') if __user__ else 'Unknown'}")
        
        # Access and modify messages
        messages = body.get("messages", [])
        
        # Example: Add a system message or modify user messages
        # messages.append({
        #     "role": "system",
        #     "content": "Additional context from filter"
        # })
        
        # Example: Log or validate messages
        for message in messages:
            print(f"Message role: {message.get('role')}, content length: {len(message.get('content', ''))}")
        
        # Return the modified body
        body["messages"] = messages
        return body

    def outlet(
        self,
        body: Dict[str, Any],
        __user__: Optional[Dict[str, Any]] = None,
        __event_emitter__=None,
        __event_call__=None,
    ) -> Dict[str, Any]:
        """
        Outlet filter - processes messages after they are received from the model.
        
        This is called after the LLM generates a response, before it's shown to the user.
        Use this to modify the response, add metadata, or perform post-processing.
        
        Args:
            body: The response body containing messages and other data
            __user__: User information (optional)
            __event_emitter__: Event emitter for streaming responses (optional)
            __event_call__: Event caller for triggering events (optional)
            
        Returns:
            Modified response body
        """
        print(f"Outlet filter called for user: {__user__.get('name', 'Unknown') if __user__ else 'Unknown'}")
        
        # Access and modify the response messages
        messages = body.get("messages", [])
        
        # Example: Modify the assistant's response
        # for message in messages:
        #     if message.get("role") == "assistant":
        #         content = message.get("content", "")
        #         message["content"] = f"{content}\n\n---\nProcessed by filter"
        
        # Example: Add metadata or logging
        for message in messages:
            print(f"Response role: {message.get('role')}, content length: {len(message.get('content', ''))}")
        
        # Return the modified body
        body["messages"] = messages
        return body
