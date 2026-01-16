# Pipe Functions Documentation

## Overview

Pipe functions in OpenWebUI are powerful components that allow you to process and transform data through a pipeline. They can intercept messages, add context, integrate external services, and modify the flow of information between users and language models.

**Official Documentation**: [https://docs.openwebui.com/features/plugin/functions](https://docs.openwebui.com/features/plugin/functions)

## What are Pipe Functions?

Pipe functions act as intermediaries in the message flow. They receive user messages, can process them, call external APIs, and return responses. They are particularly useful for:

- Integrating external AI models or services
- Adding custom preprocessing to user messages
- Implementing custom routing logic
- Creating specialized conversation flows
- Enriching messages with external data

## Structure

A basic Pipe function consists of:

1. **Class Definition**: A `Pipe` class that defines the function
2. **Valves**: Configuration parameters for the function
3. **Initialization**: Setup method that defines metadata
4. **Pipes Method**: Defines available endpoints
5. **Pipe Method**: Main processing logic

## Template Usage

The template file `pipe_function_template.py` provides a starting point for creating your own Pipe functions.

### Key Components

#### 1. Valves (Configuration)

```python
class Valves(BaseModel):
    priority: int = Field(
        default=0,
        description="Priority of the pipe function"
    )
    # Add your custom parameters here
```

Valves allow you to configure your function. Common use cases:
- API keys for external services
- Model selection parameters
- Rate limiting settings
- Feature flags

#### 2. Initialization

```python
def __init__(self):
    self.type = "pipe"
    self.id = "your_unique_id"
    self.name = "Your Function Name"
    self.valves = self.Valves()
```

Set up your function's metadata and initial configuration.

#### 3. Pipes Method

```python
def pipes(self) -> List[Dict[str, str]]:
    return [
        {
            "id": "your_pipe_id",
            "name": "Your Pipe Name"
        }
    ]
```

Define available pipes (endpoints) that users can select.

#### 4. Pipe Method (Main Logic)

```python
async def pipe(
    self,
    body: Dict[str, Any],
    __user__: Optional[Dict[str, Any]] = None,
    __event_emitter__=None,
    __event_call__=None,
) -> Union[str, Dict[str, Any]]:
    # Your processing logic here
    return response
```

This is where your main logic goes. The method receives:
- `body`: Contains messages and request data
- `__user__`: Information about the user making the request
- `__event_emitter__`: For streaming responses
- `__event_call__`: For triggering events

## Common Use Cases

### 1. External API Integration

```python
async def pipe(self, body, __user__=None, __event_emitter__=None, __event_call__=None):
    messages = body.get("messages", [])
    
    # Call external API
    response = await external_api_call(messages)
    
    return response
```

### 2. Message Preprocessing

```python
async def pipe(self, body, __user__=None, __event_emitter__=None, __event_call__=None):
    messages = body.get("messages", [])
    
    # Add context or modify messages
    enhanced_messages = add_context(messages)
    body["messages"] = enhanced_messages
    
    # Pass to next pipe or model
    return body
```

### 3. Streaming Responses

```python
async def pipe(self, body, __user__=None, __event_emitter__=None, __event_call__=None):
    if __event_emitter__:
        await __event_emitter__({
            "type": "status",
            "data": {"description": "Processing...", "done": False}
        })
    
    # Process and emit chunks
    for chunk in process_in_chunks(body):
        await __event_emitter__({
            "type": "message",
            "data": {"content": chunk}
        })
    
    await __event_emitter__({
        "type": "status",
        "data": {"description": "Complete", "done": True}
    })
    
    return ""
```

## Best Practices

1. **Error Handling**: Always wrap your logic in try-except blocks
2. **Logging**: Use print statements or proper logging for debugging
3. **Validation**: Validate input data before processing
4. **Performance**: Consider caching and optimization for frequently called functions
5. **User Context**: Use `__user__` parameter for personalization
6. **Documentation**: Add clear docstrings and comments

## Example: Simple Echo Pipe

```python
class Pipe:
    def __init__(self):
        self.type = "pipe"
        self.id = "echo_pipe"
        self.name = "Echo Pipe"
        self.valves = self.Valves()
    
    def pipes(self):
        return [{"id": "echo", "name": "Echo"}]
    
    async def pipe(self, body, __user__=None, __event_emitter__=None, __event_call__=None):
        messages = body.get("messages", [])
        if messages:
            last_content = messages[-1].get("content", "")
            return f"Echo: {last_content}"
        return "No message to echo"
```

## Testing Your Pipe Function

1. Save your function as a `.py` file
2. Upload it to OpenWebUI via Settings > Functions
3. Enable the function
4. Test it in a chat by selecting your pipe from the model dropdown

## Additional Resources

- **Official Documentation**: [https://docs.openwebui.com/features/plugin/functions](https://docs.openwebui.com/features/plugin/functions)
- **Community Examples**: Check the OpenWebUI community for more examples
- **Template File**: `templates/pipe_function_template.py`

## Troubleshooting

**Function not appearing in UI**: Check that the class is named `Pipe` and `pipes()` method returns valid pipe definitions

**Import errors**: Ensure all required packages are available in OpenWebUI's environment

**Async issues**: Make sure to use `async`/`await` properly when calling asynchronous functions

**Event emitter not working**: Verify that `__event_emitter__` is not None before calling it
