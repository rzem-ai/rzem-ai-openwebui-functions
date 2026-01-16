# Filter Functions Documentation

## Overview

Filter functions in OpenWebUI are middleware components that intercept and modify messages before and after they are processed by the language model. They provide powerful capabilities for content moderation, logging, adding metadata, and transforming requests and responses.

**Official Documentation**: [https://docs.openwebui.com/features/plugin/functions](https://docs.openwebui.com/features/plugin/functions)

## What are Filter Functions?

Filter functions sit between the user and the language model, intercepting messages at two key points:

1. **Inlet**: Before messages reach the model (preprocessing)
2. **Outlet**: After the model generates a response (postprocessing)

They are particularly useful for:

- Content moderation and safety checks
- Adding context or system prompts
- Logging and analytics
- Request/response transformation
- User-specific customization
- Rate limiting and access control

## Structure

A basic Filter function consists of:

1. **Class Definition**: A `Filter` class that defines the function
2. **Valves**: Global configuration parameters
3. **UserValves**: User-specific configuration parameters
4. **Initialization**: Setup method that defines metadata
5. **Inlet Method**: Preprocesses requests before they reach the model
6. **Outlet Method**: Postprocesses responses before they reach the user

## Template Usage

The template file `filter_function_template.py` provides a starting point for creating your own Filter functions.

### Key Components

#### 1. Valves (Global Configuration)

```python
class Valves(BaseModel):
    priority: int = Field(
        default=0,
        description="Priority of the filter function"
    )
    # Add your custom parameters here
```

Valves define global configuration that applies to all users. Common use cases:
- Feature flags
- API endpoints
- Global settings
- Moderation thresholds

#### 2. UserValves (User-Specific Configuration)

```python
class UserValves(BaseModel):
    # Add user-specific parameters here
    pass
```

UserValves allow per-user customization. Common use cases:
- User preferences
- Language settings
- Personal API keys
- Custom prompts

#### 3. Initialization

```python
def __init__(self):
    self.type = "filter"
    self.id = "your_filter_id"
    self.name = "Your Filter Name"
    self.valves = self.Valves()
```

Set up your filter's metadata and initial configuration.

#### 4. Inlet Method (Preprocessing)

```python
def inlet(
    self,
    body: Dict[str, Any],
    __user__: Optional[Dict[str, Any]] = None,
    __event_emitter__=None,
    __event_call__=None,
) -> Dict[str, Any]:
    # Modify messages before they reach the model
    messages = body.get("messages", [])
    # ... processing logic ...
    body["messages"] = messages
    return body
```

The inlet method is called when a user sends a message, before it reaches the LLM.

#### 5. Outlet Method (Postprocessing)

```python
def outlet(
    self,
    body: Dict[str, Any],
    __user__: Optional[Dict[str, Any]] = None,
    __event_emitter__=None,
    __event_call__=None,
) -> Dict[str, Any]:
    # Modify responses after the model generates them
    messages = body.get("messages", [])
    # ... processing logic ...
    body["messages"] = messages
    return body
```

The outlet method is called after the LLM generates a response, before it's shown to the user.

## Common Use Cases

### 1. Adding System Context (Inlet)

```python
def inlet(self, body, __user__=None, __event_emitter__=None, __event_call__=None):
    messages = body.get("messages", [])
    
    # Add a system message with context
    messages.insert(0, {
        "role": "system",
        "content": "You are a helpful assistant. Always be concise."
    })
    
    body["messages"] = messages
    return body
```

### 2. Content Moderation (Inlet)

```python
def inlet(self, body, __user__=None, __event_emitter__=None, __event_call__=None):
    messages = body.get("messages", [])
    
    for message in messages:
        content = message.get("content", "")
        if contains_inappropriate_content(content):
            # Block or modify the message
            message["content"] = "[Content removed by filter]"
    
    body["messages"] = messages
    return body
```

### 3. Response Enhancement (Outlet)

```python
def outlet(self, body, __user__=None, __event_emitter__=None, __event_call__=None):
    messages = body.get("messages", [])
    
    for message in messages:
        if message.get("role") == "assistant":
            content = message.get("content", "")
            # Add citations or sources
            message["content"] = f"{content}\n\n[Response generated at {datetime.now()}]"
    
    body["messages"] = messages
    return body
```

### 4. Logging and Analytics

```python
def inlet(self, body, __user__=None, __event_emitter__=None, __event_call__=None):
    # Log the incoming request
    user_name = __user__.get("name", "Unknown") if __user__ else "Unknown"
    log_request(user_name, body.get("messages", []))
    
    return body

def outlet(self, body, __user__=None, __event_emitter__=None, __event_call__=None):
    # Log the outgoing response
    user_name = __user__.get("name", "Unknown") if __user__ else "Unknown"
    log_response(user_name, body.get("messages", []))
    
    return body
```

### 5. User-Specific Customization

```python
class Filter:
    class UserValves(BaseModel):
        language: str = Field(default="en", description="Preferred language")
        tone: str = Field(default="professional", description="Response tone")
    
    def inlet(self, body, __user__=None, __event_emitter__=None, __event_call__=None):
        messages = body.get("messages", [])
        
        # Get user preferences
        user_valves = __user__.get("valves", self.UserValves())
        
        # Add user-specific instruction
        messages.insert(0, {
            "role": "system",
            "content": f"Respond in {user_valves.language} with a {user_valves.tone} tone."
        })
        
        body["messages"] = messages
        return body
```

## Best Practices

1. **Always Return the Body**: Both inlet and outlet must return the body dict
2. **Immutable Operations**: Be careful when modifying shared objects
3. **Error Handling**: Wrap logic in try-except blocks to prevent breaking the pipeline
4. **Performance**: Keep filters lightweight; they run on every message
5. **User Privacy**: Be mindful of logging sensitive user data
6. **Priority**: Use priority to control filter execution order (higher = runs earlier)

## Message Structure

Messages in the body follow this structure:

```python
{
    "messages": [
        {
            "role": "user" | "assistant" | "system",
            "content": "Message content",
            # Optional fields:
            "name": "Username",
            "timestamp": 1234567890
        }
    ],
    "model": "model_name",
    # Other request-specific fields
}
```

## Example: Simple Content Filter

```python
class Filter:
    def __init__(self):
        self.type = "filter"
        self.id = "content_filter"
        self.name = "Content Filter"
        self.valves = self.Valves()
    
    def inlet(self, body, __user__=None, __event_emitter__=None, __event_call__=None):
        messages = body.get("messages", [])
        
        # Filter out messages containing banned words
        banned_words = ["spam", "advertisement"]
        
        for message in messages:
            content = message.get("content", "").lower()
            for word in banned_words:
                if word in content:
                    message["content"] = "[Filtered: inappropriate content]"
                    break
        
        body["messages"] = messages
        return body
    
    def outlet(self, body, __user__=None, __event_emitter__=None, __event_call__=None):
        # No outlet processing needed for this example
        return body
```

## Filter Execution Order

Filters are executed in priority order:
1. Higher priority filters run first in the inlet phase
2. Higher priority filters run last in the outlet phase

This allows you to control the order of preprocessing and postprocessing.

## Testing Your Filter Function

1. Save your function as a `.py` file
2. Upload it to OpenWebUI via Settings > Functions
3. Enable the function
4. Test it in a chat - your filter will automatically process all messages

## Additional Resources

- **Official Documentation**: [https://docs.openwebui.com/features/plugin/functions](https://docs.openwebui.com/features/plugin/functions)
- **Community Examples**: Check the OpenWebUI community for more examples
- **Template File**: `templates/filter_function_template.py`

## Troubleshooting

**Filter not executing**: Check that the class is named `Filter` and both `inlet` and `outlet` methods are defined

**Messages not modified**: Ensure you're returning the modified `body` from both methods

**Breaking the pipeline**: Make sure your filter doesn't raise unhandled exceptions

**Priority not working**: Verify the priority value in Valves is set correctly (higher = runs earlier)

**User valves not applying**: Check that UserValves are properly defined and accessed from `__user__` parameter
