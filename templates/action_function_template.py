"""
Title: Action Function Template
Author: Your Name
Version: 0.1.0
License: MIT
Description: Template for creating OpenWebUI Action Functions
"""

from typing import Optional, Dict, Any, Callable, Awaitable
from pydantic import BaseModel, Field


class Action:
    """
    OpenWebUI Action Function Template
    
    Action functions provide custom actions that can be triggered by the UI or other functions.
    They can be used to perform operations like file uploads, API calls, or custom workflows.
    """

    class Valves(BaseModel):
        """
        Valves are used to configure the action function.
        Add any configuration parameters your function needs here.
        """
        priority: int = Field(
            default=0,
            description="Priority of the action function"
        )
        # Add your custom configuration parameters here
        # Example:
        # api_endpoint: str = Field(default="", description="API endpoint URL")

    class UserValves(BaseModel):
        """
        User-specific valves that can be configured per user.
        These settings override the global Valves for specific users.
        """
        pass
        # Add user-specific configuration parameters here
        # Example:
        # notifications_enabled: bool = Field(default=True, description="Enable notifications")

    def __init__(self):
        """Initialize the action function with default configuration."""
        self.type = "action"
        self.id = "action_function_template"
        self.name = "Action Function Template"
        self.valves = self.Valves()

    def action(
        self,
        body: Dict[str, Any],
        __user__: Optional[Dict[str, Any]] = None,
        __event_emitter__: Optional[Callable[[dict], Awaitable[None]]] = None,
        __event_call__: Optional[Callable[[dict], Awaitable[dict]]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Main action function that performs the custom operation.
        
        This function is triggered when the action is invoked from the UI or by other functions.
        
        Args:
            body: The request body containing action parameters and data
            __user__: User information (optional)
            __event_emitter__: Event emitter for sending events (optional)
            __event_call__: Event caller for triggering other events (optional)
            
        Returns:
            Result of the action (dict or None)
        """
        print(f"Action called by user: {__user__.get('name', 'Unknown') if __user__ else 'Unknown'}")
        
        # Extract parameters from body
        action_type = body.get("action", "default")
        parameters = body.get("parameters", {})
        
        # Perform the action based on type
        if action_type == "process":
            result = self._process_action(parameters, __user__)
        elif action_type == "execute":
            result = self._execute_action(parameters, __user__)
        else:
            result = {
                "success": False,
                "message": f"Unknown action type: {action_type}"
            }
        
        return result

    def _process_action(
        self,
        parameters: Dict[str, Any],
        user: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process action implementation.
        
        Args:
            parameters: Action parameters
            user: User information
            
        Returns:
            Action result
        """
        # Implement your process logic here
        print(f"Processing with parameters: {parameters}")
        
        return {
            "success": True,
            "message": "Process action completed",
            "data": parameters
        }

    def _execute_action(
        self,
        parameters: Dict[str, Any],
        user: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute action implementation.
        
        Args:
            parameters: Action parameters
            user: User information
            
        Returns:
            Action result
        """
        # Implement your execute logic here
        print(f"Executing with parameters: {parameters}")
        
        return {
            "success": True,
            "message": "Execute action completed",
            "data": parameters
        }
