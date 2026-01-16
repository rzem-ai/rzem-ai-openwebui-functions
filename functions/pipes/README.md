# Pipe Functions

This directory contains production-ready pipe function implementations for OpenWebUI.

## Available Pipes

### fal.ai Image Generator

**File**: [`fal-ai-image-generation-pipe.py`](fal-ai-image-generation-pipe.py)

A unified pipe function for generating images using various fal.ai models. This manifold pipe supports multiple image generation models with dynamic parameter overrides through prompt tags.

#### Features

- **Multiple Model Support**: Includes Flux.1, Flux.2, NanoBanana, Z-Image models and variants
- **Prompt Tag Syntax**: Override generation parameters directly in prompts using command-line style tags
- **Flexible Configuration**: Configure defaults via valves, override per-request via tags
- **Safety Controls**: Optional safety checker integration
- **Multi-Image Generation**: Generate multiple images in a single request

#### Supported Models

- **Flux.1**: dev, kontext-dev, pro, pro-kontext
- **Flux.2**: dev, flex, pro, klein-4b
- **NanoBanana**: pro
- **Z-Image**: turbo

#### Prompt Tag Syntax

Override generation parameters by including tags in your prompt. Tags use the format `--tagname value` or `—tagname value` (with em dash).

**Supported Tags**:

| Tag | Type | Description | Example |
|-----|------|-------------|---------|
| `--ar` | ratio | Aspect ratio | `--ar 16:9`, `--ar 1:1` |
| `--steps` | int | Number of inference steps | `--steps 24`, `--steps 50` |
| `--seed` | int | Random seed for reproducibility | `--seed 42` |
| `--guide` | float | Guidance scale | `--guide 7.5` |
| `--repeat` | int | Number of images to generate | `--repeat 2`, `--repeat 4` |
| `--safe` | bool | Enable safety checker | `--safe`, `--safe true` |
| `--format` | string | Output format | `--format png`, `--format jpeg` |
| `--speed` | string | Acceleration mode | `--speed fast`, `--speed quality` |
| `--enhance` | bool | Enhance prompt (model-specific) | `--enhance` |

**Example Prompts**:
```
a dog in a park --steps 24 --ar 16:9
portrait photo —seed 42 —guide 7.5 —safe
landscape --ar 9:16 --repeat 2 --format png
cyberpunk city --steps 50 --seed 12345 --guide 3.5 --repeat 4
```

**Notes**:
- Tags are removed from the prompt before generation
- Tags override default valve settings for that request only
- Unknown or invalid tags are ignored with a warning
- Not all tags are supported by all models (check model configuration)

#### Configuration (Valves)

| Valve | Type | Default | Description |
|-------|------|---------|-------------|
| `FAL_KEY` | string | `""` | API Key for fal.ai (required) |
| `WIDTH` | int | `800` | Default image width in pixels |
| `HEIGHT` | int | `1422` | Default image height in pixels |
| `ASPECT_RATIO` | string | `"9:16"` | Default aspect ratio for ratio-based models |
| `ENABLE_SAFETY_CHECKER` | bool | `false` | Enable safety checker by default |

#### Requirements

```
fal-client
python-dotenv
```

#### Environment Variables

- `FAL_KEY`: Your fal.ai API key (can be set via valve or environment)

#### Installation

1. **Install in OpenWebUI**:
   - Navigate to Settings > Functions
   - Click "+" to add a new function
   - Copy and paste the contents of `fal-ai-image-generation-pipe.py`
   - Save the function

2. **Configure API Key**:
   - After installation, click on the function settings
   - Enter your fal.ai API key in the `FAL_KEY` valve
   - Adjust other valves as needed (dimensions, aspect ratio, etc.)

3. **Select Model**:
   - In a chat, select one of the "Fal.ai Master: " models from the model dropdown
   - The manifold pipe exposes each supported model as a separate selectable option

#### Usage Examples

**Basic Usage**:
```
Generate a beautiful sunset over mountains
```

**With Custom Parameters**:
```
A futuristic cityscape --steps 30 --ar 16:9 --seed 42
```

**Multiple Images**:
```
Portrait of a smiling person --repeat 4 --steps 24
```

**High Quality with Safety**:
```
Professional product photography --steps 50 --guide 7.5 --safe --format png
```

**Reproducible Generation**:
```
Abstract geometric patterns --seed 12345 --steps 30 --ar 1:1
```

#### Model-Specific Considerations

- **Aspect Ratio**: Most models support the `--ar` tag for dynamic aspect ratios
- **Enhancement**: Only some models (e.g., Flux Kontext variants) support the `--enhance` tag
- **Safety Checker**: Available on most models, can be enabled globally via valve or per-request via `--safe`
- **Acceleration**: The `--speed` tag is supported on models that offer acceleration modes

#### Troubleshooting

**No images generated**:
- Verify your `FAL_KEY` is set correctly in the valves
- Check that you've selected a model from the dropdown
- Review the error message in the chat

**Tags not working**:
- Ensure tags use proper format: `--tagname value`
- Check that the tag is supported by the selected model
- Look for warnings in the status messages

**Quality issues**:
- Increase `--steps` for better quality (e.g., `--steps 50`)
- Adjust `--guide` (guidance scale) - higher values follow prompt more closely
- Try different seeds with `--seed` to explore variations

**API errors**:
- Verify your fal.ai API key is valid and has credits
- Check fal.ai service status
- Ensure you're not exceeding rate limits

#### Version History

- **v3.0.0**: Renamed `--count` tag to `--repeat` for clarity
- **v2.x**: Added tag processor with em dash support
- **v1.x**: Initial release with multiple model support

#### License

MIT License

#### Support

For issues or questions about this pipe:
1. Check the inline documentation in the source code
2. Review fal.ai model documentation (links in source)
3. Open an issue in this repository

---

For more information about pipe functions in general, see:
- [Pipe Function Template](../../templates/pipe_function_template.py)
- [Pipe Functions Documentation](../../docs/PIPE_FUNCTIONS.md)
- [Official OpenWebUI Documentation](https://docs.openwebui.com/features/plugin/functions)
