"""
title: fal.ai Image Generator
description: A unified pipe to generate images using various fal.ai models. Requires explicit model selection.
author: Alex Rzem
version: 0.2.0
license: MIT
requirements: fal-client, python-dotenv, requests
environment_variables: FAL_KEY

PROMPT TAG SYNTAX:
==================
You can override generation parameters by including tags in your prompt.
Tags use the format: --tagname value (or —tagname value with em dash)

Supported Tags:
  --ar <ratio>      Aspect ratio (e.g., 16:9, 9:16, 1:1, 4:3, 3:4)
  --steps <int>     Number of inference steps (e.g., 24, 50)
  --seed <int>      Random seed for reproducibility (e.g., 42, 12345)
  --guide <float>   Guidance scale (e.g., 7.5, 3.5)
  --repeat <int>    Number of images to generate (e.g., 1, 2, 4)
  --safe [bool]     Enable safety checker (--safe or --safe true/false)
  --format <str>    Output format (e.g., jpeg, png)
  --speed <str>     Acceleration mode (e.g., fast, quality)
  --enhance [bool]  Enhance prompt (model-specific, e.g., --enhance)

Examples:
  "a dog in a park --steps 24 --ar 16:9"
  "portrait photo —seed 42 —guide 7.5 —safe"
  "landscape --ar 9:16 --repeat 2 --format png"

Notes:
- Tags are removed from the prompt before generation
- Tags override default valve settings for that request
- Unknown or invalid tags are ignored with a warning
- Not all tags are supported by all models (check parse_tags config)
"""

import os
import re
import asyncio
import json
import requests
from typing import List, Callable, Awaitable, AsyncGenerator
from pydantic import BaseModel, Field
import fal_client

MODELS = [
    {
        "id": "falai-flux-1-dev",
        "name": "Flux.1 [dev]",
        "path": "fal-ai/flux-1/dev",
        "schema_input": "https://fal.ai/models/fal-ai/flux-1/dev/api#schema-input",
        "schema_output": "https://fal.ai/models/fal-ai/flux-1/dev/api#schema-output",
        "parse_tags": [
            {"tag": "ar", "parameter": "image_size"},
            {"tag": "steps", "parameter": "num_inference_steps"},
            {"tag": "seed", "parameter": "seed"},
            {"tag": "guide", "parameter": "guidance_scale"},
            {"tag": "repeat", "parameter": "num_images"},
            {"tag": "safe", "parameter": "enable_safety_checker"},
            {"tag": "format", "parameter": "output_format"},
            {"tag": "speed", "parameter": "acceleration"},
        ],
    },
    {
        "id": "falai-flux-kontext-dev",
        "name": "Flux.1 Kontext [dev]",
        "path": "fal-ai/flux-kontext/dev",
        "schema_input": "https://fal.ai/models/fal-ai/flux-kontext/dev/api#schema-input",
        "schema_output": "https://fal.ai/models/fal-ai/flux-kontext/dev/api#schema-output",
        "parse_tags": [
            {"tag": "ar", "parameter": "image_size"},
            {"tag": "steps", "parameter": "num_inference_steps"},
            {"tag": "seed", "parameter": "seed"},
            {"tag": "guide", "parameter": "guidance_scale"},
            {"tag": "repeat", "parameter": "num_images"},
            {"tag": "safe", "parameter": "enable_safety_checker"},
            {"tag": "format", "parameter": "output_format"},
            {"tag": "speed", "parameter": "acceleration"},
            {"tag": "enhance", "parameter": "enhance_prompt"},
        ],
    },
    {
        "id": "falai-flux-pro",
        "name": "Flux.1 [pro]",
        "path": "fal-ai/flux-pro/v1.1",
        "schema_input": "https://fal.ai/models/fal-ai/flux-pro/v1.1/api#schema-input",
        "schema_output": "https://fal.ai/models/fal-ai/flux-pro/v1.1/api#schema-output",
        "parse_tags": [
            {"tag": "ar", "parameter": "image_size"},
            {"tag": "steps", "parameter": "num_inference_steps"},
            {"tag": "seed", "parameter": "seed"},
            {"tag": "guide", "parameter": "guidance_scale"},
            {"tag": "repeat", "parameter": "num_images"},
            {"tag": "safe", "parameter": "enable_safety_checker"},
            {"tag": "format", "parameter": "output_format"},
            {"tag": "speed", "parameter": "acceleration"},
        ],
    },
    {
        "id": "falai-flux-pro-kontext",
        "name": "Flux.1 Kontext [pro]",
        "path": "fal-ai/flux-pro/kontext",
        "schema_input": "https://fal.ai/models/fal-ai/flux-pro/kontext/api#schema-input",
        "schema_output": "ttps://fal.ai/models/fal-ai/flux-pro/kontext/api#schema-output",
        "parse_tags": [
            {"tag": "ar", "parameter": "image_size"},
            {"tag": "steps", "parameter": "num_inference_steps"},
            {"tag": "seed", "parameter": "seed"},
            {"tag": "guide", "parameter": "guidance_scale"},
            {"tag": "repeat", "parameter": "num_images"},
            {"tag": "safe", "parameter": "enable_safety_checker"},
            {"tag": "format", "parameter": "output_format"},
            {"tag": "speed", "parameter": "acceleration"},
        ],
    },
    {
        "id": "falai-flux-2",
        "name": "Flux.2 [dev]",
        "path": "fal-ai/flux-2",
        "schema_input": "https://fal.ai/models/fal-ai/flux-2/api#schema-input",
        "schema_output": "https://fal.ai/models/fal-ai/flux-2/api#schema-output",
        "parse_tags": [
            {"tag": "ar", "parameter": "image_size"},
            {"tag": "steps", "parameter": "num_inference_steps"},
            {"tag": "seed", "parameter": "seed"},
            {"tag": "guide", "parameter": "guidance_scale"},
            {"tag": "repeat", "parameter": "num_images"},
            {"tag": "safe", "parameter": "enable_safety_checker"},
            {"tag": "format", "parameter": "output_format"},
            {"tag": "speed", "parameter": "acceleration"},
        ],
    },
    {
        "id": "falai-flux-2-flex",
        "name": "Flux.2 [flex]",
        "path": "fal-ai/flux-2-flex",
        "schema_input": "https://fal.ai/models/fal-ai/flux-2-flex/api#schema-input",
        "schema_output": "https://fal.ai/models/fal-ai/flux-2-flex/api#schema-output",
        "parse_tags": [
            {"tag": "ar", "parameter": "image_size"},
            {"tag": "steps", "parameter": "num_inference_steps"},
            {"tag": "seed", "parameter": "seed"},
            {"tag": "guide", "parameter": "guidance_scale"},
            {"tag": "repeat", "parameter": "num_images"},
            {"tag": "safe", "parameter": "enable_safety_checker"},
            {"tag": "format", "parameter": "output_format"},
            {"tag": "speed", "parameter": "acceleration"},
        ],
    },
    {
        "id": "falai-flux-2-pro",
        "name": "Flux.2 [pro]",
        "path": "fal-ai/flux-2-pro",
        "schema_input": "https://fal.ai/models/fal-ai/flux-2-pro/api#schema-input",
        "schema_output": "https://fal.ai/models/fal-ai/flux-2-pro/api#schema-output",
        "parse_tags": [
            {"tag": "ar", "parameter": "image_size"},
            {"tag": "steps", "parameter": "num_inference_steps"},
            {"tag": "seed", "parameter": "seed"},
            {"tag": "guide", "parameter": "guidance_scale"},
            {"tag": "repeat", "parameter": "num_images"},
            {"tag": "safe", "parameter": "enable_safety_checker"},
            {"tag": "format", "parameter": "output_format"},
            {"tag": "speed", "parameter": "acceleration"},
        ],
    },
    {
        "id": "falai-flux-2-klein-4b",
        "name": "Flux.2 [klein] - 4b",
        "path": "fal-ai/flux-2/klein/4b",
        "schema_input": "https://fal.ai/models/fal-ai/flux-2/klein/4b/api#schema-input",
        "schema_output": "https://fal.ai/models/fal-ai/flux-2/klein/4b/api#schema-output",
        "parse_tags": [
            {"tag": "ar", "parameter": "image_size"},
            {"tag": "steps", "parameter": "num_inference_steps"},
            {"tag": "seed", "parameter": "seed"},
            {"tag": "guide", "parameter": "guidance_scale"},
            {"tag": "repeat", "parameter": "num_images"},
            {"tag": "safe", "parameter": "enable_safety_checker"},
            {"tag": "format", "parameter": "output_format"},
            {"tag": "speed", "parameter": "acceleration"},
        ],
    },
    {
        "id": "falai-nano-banana-pro",
        "name": "NanoBanana [pro]",
        "path": "fal-ai/nano-banana-pro",
        "schema_input": "https://fal.ai/models/fal-ai/nano-banana-pro/api#schema-input",
        "schema_output": "https://fal.ai/models/fal-ai/nano-banana-pro/api#schema-output",
        "parse_tags": [
            {"tag": "ar", "parameter": "image_size"},
            {"tag": "steps", "parameter": "num_inference_steps"},
            {"tag": "seed", "parameter": "seed"},
            {"tag": "guide", "parameter": "guidance_scale"},
            {"tag": "repeat", "parameter": "num_images"},
            {"tag": "safe", "parameter": "enable_safety_checker"},
            {"tag": "format", "parameter": "output_format"},
            {"tag": "speed", "parameter": "acceleration"},
        ],
    },
    {
        "id": "falai-z-image-turbo",
        "name": "Z-Image [turbo]",
        "path": "fal-ai/z-image/turbo",
        "schema_input": "https://fal.ai/models/fal-ai/z-image/turbo/api#schema-input",
        "schema_output": "https://fal.ai/models/fal-ai/z-image/turbo/api#schema-output",
        "parse_tags": [
            {"tag": "ar", "parameter": "image_size"},
            {"tag": "steps", "parameter": "num_inference_steps"},
            {"tag": "seed", "parameter": "seed"},
            {"tag": "guide", "parameter": "guidance_scale"},
            {"tag": "repeat", "parameter": "num_images"},
            {"tag": "safe", "parameter": "enable_safety_checker"},
            {"tag": "format", "parameter": "output_format"},
            {"tag": "speed", "parameter": "acceleration"},
        ],
    },
]


def parse_prompt_tags(prompt: str, model_config: dict, valves) -> tuple:
    """
    Parse command-line style tags from prompt and return cleaned prompt with overrides.

    Args:
        prompt: User prompt potentially containing tags like "--steps 24 --ar 9:16"
        model_config: Model dictionary from MODELS array with parse_tags field
        valves: Pipe valves for accessing WIDTH/HEIGHT for aspect ratio calculations

    Returns:
        tuple: (cleaned_prompt, overrides_dict)
            - cleaned_prompt: Original prompt with all tags removed
            - overrides_dict: Dictionary of parameter overrides, may contain "_warnings" list

    Example:
        >>> parse_prompt_tags("dog --steps 24 --ar 16:9", model_config, valves)
        ("dog", {"num_inference_steps": 24, "image_size": {"width": 1422, "height": 800}})
    """
    overrides = {}
    warnings = []
    cleaned_prompt = prompt

    # Get parse_tags configuration for this model
    parse_tags_config = model_config.get("parse_tags", [])
    if not parse_tags_config:
        return prompt, overrides

    # Build a mapping of tag -> parameter name
    tag_map = {item["tag"]: item["parameter"] for item in parse_tags_config}

    # Pattern to match tags: --tagname or —tagname or --tagname value or —tagname value
    # This regex captures: (?:--|—)(\w+)(?:\s+([^\s\-—][^\-—]*?))?(?=\s+(?:--|—)|$)
    # Matches "--steps 24", "—steps 24", "--safe", "—safe", "--ar 16:9", "—ar 16:9", etc.
    tag_pattern = r"(?:--|—)(\w+)(?:\s+([^\s\-—][^\-—]*?))?(?=\s+(?:--|—)|$)"

    matches = list(re.finditer(tag_pattern, prompt))

    for match in matches:
        tag_name = match.group(1)
        tag_value = match.group(2)

        # Check if tag is valid for this model
        if tag_name not in tag_map:
            warnings.append(f"Unknown tag --{tag_name} ignored")
            continue

        parameter_name = tag_map[tag_name]

        # Convert value based on parameter type
        try:
            converted_value = _convert_tag_value(
                tag_name, tag_value, parameter_name, valves
            )
            overrides[parameter_name] = converted_value
        except ValueError as e:
            warnings.append(str(e))
            continue

    # Remove all tags from the prompt
    cleaned_prompt = re.sub(tag_pattern, "", prompt)
    # Clean up extra whitespace
    cleaned_prompt = re.sub(r"\s+", " ", cleaned_prompt).strip()

    if warnings:
        overrides["_warnings"] = warnings

    return cleaned_prompt, overrides


def _convert_tag_value(
    tag_name: str, tag_value: str | None, parameter_name: str, valves
):
    """
    Convert a tag value string to the appropriate type based on parameter name.

    Args:
        tag_name: Original tag name (e.g., "steps", "ar")
        tag_value: String value from prompt or None for flag-only tags
        parameter_name: API parameter name (e.g., "num_inference_steps", "image_size")
        valves: Pipe valves for WIDTH/HEIGHT access

    Returns:
        Converted value in appropriate type

    Raises:
        ValueError: If conversion fails or value is invalid
    """
    # Handle boolean parameters (flags)
    if parameter_name in ["enable_safety_checker", "enhance_prompt"]:
        if tag_value is None:
            return True

        tag_value_lower = tag_value.strip().lower()
        if tag_value_lower in ["true", "1", "yes"]:
            return True
        elif tag_value_lower in ["false", "0", "no"]:
            return False
        else:
            raise ValueError(
                f"Invalid boolean value '{tag_value}' for --{tag_name}, skipping"
            )

    # All other parameters require a value
    if tag_value is None:
        raise ValueError(f"Tag --{tag_name} requires a value, skipping")

    tag_value = tag_value.strip()

    # Handle aspect ratio -> image_size conversion
    if parameter_name == "image_size":
        return _convert_aspect_ratio(tag_value, tag_name, valves)

    # Handle integer parameters
    if parameter_name in ["num_inference_steps", "num_images", "seed"]:
        try:
            return int(tag_value)
        except ValueError:
            raise ValueError(
                f"Invalid integer value '{tag_value}' for --{tag_name}, skipping"
            )

    # Handle float parameters
    if parameter_name == "guidance_scale":
        try:
            return float(tag_value)
        except ValueError:
            raise ValueError(
                f"Invalid float value '{tag_value}' for --{tag_name}, skipping"
            )

    # Handle string parameters (output_format, acceleration, etc.)
    return tag_value


def _convert_aspect_ratio(ratio_str: str, tag_name: str, valves) -> dict:
    """
    Convert aspect ratio string like "16:9" to image_size dict.

    Uses valve WIDTH and HEIGHT as base dimensions, adjusting one to match ratio.

    Args:
        ratio_str: Aspect ratio string like "16:9", "9:16", "1:1"
        tag_name: Original tag name for error messages
        valves: Pipe valves containing WIDTH and HEIGHT

    Returns:
        dict: {"width": int, "height": int}

    Raises:
        ValueError: If ratio format is invalid
    """
    # Parse ratio like "16:9" or "9:16"
    match = re.match(r"^(\d+):(\d+)$", ratio_str.strip())
    if not match:
        raise ValueError(
            f"Invalid aspect ratio '{ratio_str}' for --{tag_name}, expected format like '16:9', skipping"
        )

    width_ratio = int(match.group(1))
    height_ratio = int(match.group(2))

    if width_ratio <= 0 or height_ratio <= 0:
        raise ValueError(
            f"Invalid aspect ratio '{ratio_str}' for --{tag_name}, skipping"
        )

    # Get base dimensions from valves
    base_width = valves.WIDTH
    base_height = valves.HEIGHT

    # Calculate dimensions preserving the requested ratio
    # If width_ratio > height_ratio, we have a landscape/wider aspect
    # If height_ratio > width_ratio, we have a portrait/taller aspect

    ratio_value = width_ratio / height_ratio
    base_ratio = base_width / base_height

    if ratio_value > base_ratio:
        # Requested ratio is wider than base, adjust width up
        final_width = int(base_height * ratio_value)
        final_height = base_height
    else:
        # Requested ratio is taller than base, adjust height up
        final_width = base_width
        final_height = int(base_width / ratio_value)

    return {"width": final_width, "height": final_height}


class Pipe:
    class Valves(BaseModel):
        FAL_KEY: str = Field(default="", description="API Key for Fal.ai (required)")
        # Dimensions for models that use exact pixels (Flux 2, Hunyuan, SeaDream, Z-Image)
        WIDTH: int = Field(default=800, description="Width")
        HEIGHT: int = Field(default=1422, description="Height")
        # Aspect Ratio for models that use ratios (Flux Ultra, Imagen 4, Recraft)
        ASPECT_RATIO: str = Field(
            default="9:16",
            description="Aspect Ratio. Options: 16:9, 1:1, 9:16, 4:3, 3:4",
        )

        ENABLE_SAFETY_CHECKER: bool = Field(
            default=False, description="Enable Safety Checker"
        )

        # OpenRouter configuration for tag generation
        OPENROUTER_API_KEY: str = Field(
            default="", description="API Key for OpenRouter (required for tag generation)"
        )
        TAG_MODEL: str = Field(
            default="qwen/qwen-3-vl-32b-instruct",
            description="Model to use for tag generation via OpenRouter"
        )

    def __init__(self):
        self.type = "manifold"
        self.id = "openwebui_function_fal_ai"
        self.name = "Fal.ai Image Generator"
        self.description = "A unified pipe to generate images using various Fal.ai models. Requires explicit model selection."
        self.valves = self.Valves()
        self.emitter: Callable[[dict], Awaitable[None]] | None = None

    async def emit_status(self, message: str = "", done: bool = False):
        if self.emitter:
            try:
                await self.emitter(
                    {
                        "type": "status",
                        "data": {
                            "description": message,
                            "done": done,
                        },
                    }
                )
            except Exception:
                pass

    def is_tag_generation_request(self, user_message: str) -> bool:
        """
        Detect if the request is for tag generation based on specific patterns.

        Args:
            user_message: The user message content to check

        Returns:
            bool: True if this is a tag generation request, False otherwise
        """
        if not user_message:
            return False

        message_lower = user_message.lower()

        # Check for tag generation indicators
        has_task_generate = "### task: generate" in message_lower
        has_tags_keyword = "tags" in message_lower
        has_tags_json = '"tags":' in user_message
        has_categorizing = "categorizing the main themes" in message_lower

        # Debug logging
        print(f"[Tag Detection] Checking message for tag generation patterns...")
        print(f"[Tag Detection] Has '### Task: Generate': {has_task_generate}")
        print(f"[Tag Detection] Has 'tags' keyword: {has_tags_keyword}")
        print(f"[Tag Detection] Has '\"tags\":' JSON: {has_tags_json}")
        print(f"[Tag Detection] Has 'categorizing the main themes': {has_categorizing}")

        # Return True if message contains tag generation indicators
        is_tag_request = (has_task_generate and has_tags_keyword) or has_tags_json or has_categorizing
        print(f"[Tag Detection] Is tag generation request: {is_tag_request}")

        return is_tag_request

    def generate_tags_with_openrouter(self, messages: List[dict]) -> str:
        """
        Generate tags using OpenRouter's Qwen model.

        Args:
            messages: List of message dictionaries to send to OpenRouter

        Returns:
            str: JSON string with generated tags
        """
        print("[OpenRouter] Starting tag generation...")

        if not self.valves.OPENROUTER_API_KEY:
            print("[OpenRouter] Error: OPENROUTER_API_KEY not set")
            return '{"tags": ["Image Generation", "Art"]}'

        try:
            url = "https://openrouter.ai/api/v1/chat/completions"

            headers = {
                "Authorization": f"Bearer {self.valves.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://openwebui.com",
                "X-Title": "OpenWebUI Tag Generation"
            }

            payload = {
                "model": self.valves.TAG_MODEL,
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 200
            }

            print(f"[OpenRouter] Calling API with model: {self.valves.TAG_MODEL}")
            print(f"[OpenRouter] Payload: {json.dumps(payload, indent=2)}")

            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()
            print(f"[OpenRouter] Response: {json.dumps(result, indent=2)}")

            # Extract content from response
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0].get("message", {}).get("content", "")
                print(f"[OpenRouter] Generated content: {content}")
                return content
            else:
                print("[OpenRouter] No choices in response, using fallback")
                return '{"tags": ["Image Generation", "Art"]}'

        except requests.exceptions.Timeout:
            print("[OpenRouter] Request timeout, using fallback")
            return '{"tags": ["Image Generation", "Art"]}'
        except requests.exceptions.RequestException as e:
            print(f"[OpenRouter] Request error: {e}, using fallback")
            return '{"tags": ["Image Generation", "Art"]}'
        except Exception as e:
            print(f"[OpenRouter] Unexpected error: {e}, using fallback")
            return '{"tags": ["Image Generation", "Art"]}'

    def pipes(self) -> List[dict]:
        return [{"id": model["id"], "name": model["name"]} for model in MODELS]

    async def pipe(
        self,
        body: dict,
        __event_emitter__: Callable[[dict], Awaitable[None]] = None,
    ) -> AsyncGenerator[str, None]:
        self.emitter = __event_emitter__

        # 0. Check if this is a tag generation request
        messages = body.get("messages", [])
        if messages:
            # Get the last user message
            last_user_message = ""
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    content = msg.get("content")
                    if isinstance(content, list):
                        text_parts = [
                            p.get("text", "") for p in content if p.get("type") == "text"
                        ]
                        last_user_message = " ".join(text_parts).strip()
                    elif isinstance(content, str):
                        last_user_message = content
                    break

            # Check if this is a tag generation request
            if self.is_tag_generation_request(last_user_message):
                print("[Pipe] Detected tag generation request, routing to OpenRouter...")
                await self.emit_status("Generating tags with OpenRouter...", done=False)

                # Generate tags using OpenRouter
                tags_result = self.generate_tags_with_openrouter(messages)

                await self.emit_status("Tag generation complete", done=True)
                yield tags_result
                return

        # 1. Determine Model ID
        request_model_id = body.get("model", "")

        # Map internal IDs to Fal API IDs from global MODELS
        model_map = {model["id"]: model["path"] for model in MODELS}

        api_model_id = None

        # Check for known models
        for internal_id, external_id in model_map.items():
            if internal_id in request_model_id:
                api_model_id = external_id
                break

        # If no match found, return ERROR immediately
        if not api_model_id:
            yield f"**Error:** The selected model (`{request_model_id}`) is not supported by the Fal.ai Master Pipe.\n\nPlease select one of the **IMG:** models from the dropdown list."
            return

        # 2. Get Prompt
        messages = body.get("messages", [])
        if not messages:
            yield "Error: No messages found."
            return

        prompt = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                content = msg.get("content")
                if isinstance(content, list):
                    text_parts = [
                        p.get("text", "") for p in content if p.get("type") == "text"
                    ]
                    prompt = " ".join(text_parts).strip()
                elif isinstance(content, str):
                    prompt = content
                break

        if not prompt:
            yield "Error: No prompt found."
            return

        # 2.5. Parse Prompt Tags
        # Find model config from MODELS array
        model_config = None
        for model in MODELS:
            if model["path"] == api_model_id:
                model_config = model
                break

        # Parse tags if model config found
        cleaned_prompt = prompt
        tag_overrides = {}

        if model_config:
            cleaned_prompt, tag_overrides = parse_prompt_tags(
                prompt, model_config, self.valves
            )

            # Emit warnings if any
            if "_warnings" in tag_overrides:
                for warning in tag_overrides["_warnings"]:
                    await self.emit_status(f"Warning: {warning}", done=False)
                del tag_overrides["_warnings"]
        else:
            # Log if we couldn't find model config for tag parsing
            await self.emit_status(
                f"Note: Tag parsing not available for model {api_model_id}", done=False
            )

        # 3. Setup Env
        if not self.valves.FAL_KEY:
            yield "Error: FAL_KEY not set in valves."
            return
        os.environ["FAL_KEY"] = self.valves.FAL_KEY

        # 4. Construct Arguments
        # Start with valve defaults
        arguments = {
            "prompt": cleaned_prompt,  # Use cleaned prompt with tags removed
            "enable_safety_checker": self.valves.ENABLE_SAFETY_CHECKER,
        }

        # Logic Branches based on selected model
        if "imagen4" in api_model_id:
            arguments["aspect_ratio"] = self.valves.ASPECT_RATIO
        elif "nano-banana" in api_model_id:
            arguments["aspect_ratio"] = self.valves.ASPECT_RATIO
        else:
            # Fallback for known models that might not have a specific block above
            arguments["image_size"] = {
                "width": self.valves.WIDTH,
                "height": self.valves.HEIGHT,
            }

        # Apply tag overrides (tags take precedence over valves)
        arguments.update(tag_overrides)

        # 5. Call API
        await self.emit_status(f"Generating image with {api_model_id}...", done=False)

        try:
            loop = asyncio.get_running_loop()

            def run_fal_generation():
                return fal_client.submit(api_model_id, arguments=arguments).get()

            result = await loop.run_in_executor(None, run_fal_generation)

            if result and "images" in result and len(result["images"]) > 0:
                images = result["images"]
                num_images = len(images)

                await self.emit_status(
                    f"Generated {num_images} image{'s' if num_images > 1 else ''} successfully",
                    done=True,
                )

                # Display all generated images
                for idx, image in enumerate(images, 1):
                    image_url = image.get("url", "")
                    if image_url:
                        if num_images > 1:
                            yield f"**Image {idx}/{num_images}**\n\n"
                        yield f"![Generated Image]({image_url})\n\n"
                    else:
                        yield f"Warning: Image {idx} URL missing\n\n"
            else:
                await self.emit_status("Generation failed", done=True)
                yield f"Error: Generation failed. Result: {result}"

        except Exception as e:
            await self.emit_status(f"Error: {e}", done=True)
            yield f"Error: {e}"
