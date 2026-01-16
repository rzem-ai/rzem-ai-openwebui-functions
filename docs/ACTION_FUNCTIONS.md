# Action Functions Documentation

## Overview

Action functions in OpenWebUI provide custom actions that can be triggered by the UI or other functions. They enable you to perform specific operations like file uploads, API calls, data processing, or custom workflows that go beyond simple message processing.

**Official Documentation**: [https://docs.openwebui.com/features/plugin/functions](https://docs.openwebui.com/features/plugin/functions)

## What are Action Functions?

Action functions are event-driven components that execute specific operations when triggered. Unlike Pipe and Filter functions that process every message, Action functions are explicitly invoked when needed.

They are particularly useful for:

- File upload and processing
- External API integrations
- Database operations
- Custom workflow execution
- Background tasks
- User-initiated operations
- Data export and import

## Structure

A basic Action function consists of:

1. **Class Definition**: An `Action` class that defines the function
2. **Valves**: Global configuration parameters
3. **UserValves**: User-specific configuration parameters
4. **Initialization**: Setup method that defines metadata
5. **Action Method**: Main logic that performs the operation

## Template Usage

The template file `action_function_template.py` provides a starting point for creating your own Action functions.

### Key Components

#### 1. Valves (Global Configuration)

```python
class Valves(BaseModel):
    priority: int = Field(
        default=0,
        description="Priority of the action function"
    )
    # Add your custom parameters here
```

Valves define global configuration for the action. Common use cases:
- API endpoints and credentials
- Feature flags
- Rate limits
- Default settings

#### 2. UserValves (User-Specific Configuration)

```python
class UserValves(BaseModel):
    # Add user-specific parameters here
    pass
```

UserValves allow per-user customization. Common use cases:
- User permissions
- Personal settings
- User-specific API keys
- Notification preferences

#### 3. Initialization

```python
def __init__(self):
    self.type = "action"
    self.id = "your_action_id"
    self.name = "Your Action Name"
    self.valves = self.Valves()
```

Set up your action's metadata and initial configuration.

#### 4. Action Method (Main Logic)

```python
def action(
    self,
    body: Dict[str, Any],
    __user__: Optional[Dict[str, Any]] = None,
    __event_emitter__: Optional[Callable[[dict], Awaitable[None]]] = None,
    __event_call__: Optional[Callable[[dict], Awaitable[dict]]] = None,
) -> Optional[Dict[str, Any]]:
    # Your action logic here
    return result
```

This is where your main action logic goes. The method receives:
- `body`: Contains action parameters and data
- `__user__`: Information about the user triggering the action
- `__event_emitter__`: For emitting events
- `__event_call__`: For calling other events

## Common Use Cases

### 1. File Upload Action

```python
def action(self, body, __user__=None, __event_emitter__=None, __event_call__=None):
    file_data = body.get("file")
    
    if not file_data:
        return {"success": False, "message": "No file provided"}
    
    # Process the file
    try:
        result = process_file(file_data)
        return {
            "success": True,
            "message": "File processed successfully",
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error processing file: {str(e)}"
        }
```

### 2. External API Call

```python
def action(self, body, __user__=None, __event_emitter__=None, __event_call__=None):
    api_endpoint = self.valves.api_endpoint
    parameters = body.get("parameters", {})
    
    try:
        response = requests.post(api_endpoint, json=parameters)
        response.raise_for_status()
        
        return {
            "success": True,
            "message": "API call successful",
            "data": response.json()
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"API call failed: {str(e)}"
        }
```

### 3. Data Export Action

```python
def action(self, body, __user__=None, __event_emitter__=None, __event_call__=None):
    export_format = body.get("format", "json")
    data = body.get("data", [])
    
    try:
        if export_format == "json":
            exported = json.dumps(data, indent=2)
        elif export_format == "csv":
            exported = convert_to_csv(data)
        else:
            return {
                "success": False,
                "message": f"Unsupported format: {export_format}"
            }
        
        return {
            "success": True,
            "message": "Data exported successfully",
            "data": exported,
            "format": export_format
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Export failed: {str(e)}"
        }
```

### 4. Background Task

```python
import asyncio

class Action:
    def action(self, body, __user__=None, __event_emitter__=None, __event_call__=None):
        task_params = body.get("parameters", {})
        
        # Start background task
        asyncio.create_task(self._background_task(task_params, __event_emitter__))
        
        return {
            "success": True,
            "message": "Background task started",
            "task_id": generate_task_id()
        }
    
    async def _background_task(self, params, event_emitter):
        # Perform long-running operation
        for i in range(10):
            await asyncio.sleep(1)
            if event_emitter:
                await event_emitter({
                    "type": "progress",
                    "data": {"progress": (i + 1) * 10}
                })
```

### 5. User Permission Check

```python
def action(self, body, __user__=None, __event_emitter__=None, __event_call__=None):
    # Check user permissions
    if not __user__ or not self._has_permission(__user__, "execute"):
        return {
            "success": False,
            "message": "Insufficient permissions"
        }
    
    # Proceed with action
    result = self._execute_privileged_action(body)
    
    return {
        "success": True,
        "message": "Action executed",
        "data": result
    }

def _has_permission(self, user, permission):
    user_role = user.get("role", "user")
    return user_role in ["admin", "moderator"]
```

## Best Practices

1. **Error Handling**: Always wrap logic in try-except blocks and return meaningful error messages
2. **Return Structure**: Return a dict with `success` and `message` keys for consistency
3. **User Validation**: Check user permissions before executing sensitive operations
4. **Logging**: Log action execution for audit trails
5. **Async Operations**: Use async/await for long-running tasks
6. **Event Emission**: Use `__event_emitter__` to provide progress updates
7. **Input Validation**: Validate all input parameters before processing

## Response Structure

Actions should return a dictionary with at least:

```python
{
    "success": True | False,
    "message": "Description of the result",
    "data": {}  # Optional: additional data
}
```

## Event Emitter Usage

Use the event emitter to provide real-time feedback:

```python
if __event_emitter__:
    await __event_emitter__({
        "type": "status",  # or "progress", "message", etc.
        "data": {
            "description": "Processing...",
            "done": False
        }
    })
```

## Example: Simple Calculator Action

```python
class Action:
    def __init__(self):
        self.type = "action"
        self.id = "calculator"
        self.name = "Calculator Action"
        self.valves = self.Valves()
    
    def action(self, body, __user__=None, __event_emitter__=None, __event_call__=None):
        operation = body.get("operation")
        num1 = body.get("num1", 0)
        num2 = body.get("num2", 0)
        
        try:
            if operation == "add":
                result = num1 + num2
            elif operation == "subtract":
                result = num1 - num2
            elif operation == "multiply":
                result = num1 * num2
            elif operation == "divide":
                if num2 == 0:
                    return {
                        "success": False,
                        "message": "Division by zero"
                    }
                result = num1 / num2
            else:
                return {
                    "success": False,
                    "message": f"Unknown operation: {operation}"
                }
            
            return {
                "success": True,
                "message": "Calculation complete",
                "data": {
                    "operation": operation,
                    "result": result
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Calculation error: {str(e)}"
            }
```

## Action Invocation

Actions can be invoked in several ways:

1. **From UI**: User-triggered actions via buttons or menus
2. **From Other Functions**: Called by Pipe or Filter functions using `__event_call__`
3. **Programmatically**: Via API or custom integrations

## Testing Your Action Function

1. Save your function as a `.py` file
2. Upload it to OpenWebUI via Settings > Functions
3. Enable the function
4. Trigger the action from the UI or via API
5. Verify the returned result structure

## Debugging

Use print statements or proper logging to debug:

```python
def action(self, body, __user__=None, __event_emitter__=None, __event_call__=None):
    print(f"Action called with body: {body}")
    print(f"User: {__user__.get('name') if __user__ else 'None'}")
    
    # Your logic here
    
    print(f"Returning result: {result}")
    return result
```

## Additional Resources

- **Official Documentation**: [https://docs.openwebui.com/features/plugin/functions](https://docs.openwebui.com/features/plugin/functions)
- **Community Examples**: Check the OpenWebUI community for more examples
- **Template File**: `templates/action_function_template.py`

## Troubleshooting

**Action not appearing**: Check that the class is named `Action` and has an `action` method

**Errors not showing**: Make sure you're returning a proper result dictionary

**Event emitter not working**: Verify that `__event_emitter__` is not None and is being awaited

**Permissions issues**: Ensure you're checking `__user__` for required permissions

**Async errors**: If using async operations, make sure the action method is properly handling awaits
