# rzem-ai-openwebui-functions

A collection of custom functions for OpenWebUI, including templates and documentation for Pipe Functions, Filter Functions, and Action Functions.

## Overview

This repository provides ready-to-use templates and comprehensive documentation for developing custom OpenWebUI functions. Whether you're building data pipelines, content filters, or custom actions, these templates will help you get started quickly.

**Official OpenWebUI Documentation**: [https://docs.openwebui.com/features/plugin/functions](https://docs.openwebui.com/features/plugin/functions)

## Function Types

OpenWebUI supports three main types of functions:

### 1. Pipe Functions
Pipe functions process and transform data through a pipeline. They can intercept messages, add context, integrate external services, and modify the flow of information between users and language models.

- **Template**: [`templates/pipe_function_template.py`](templates/pipe_function_template.py)
- **Documentation**: [`docs/PIPE_FUNCTIONS.md`](docs/PIPE_FUNCTIONS.md)

**Use cases**: External API integration, message preprocessing, custom routing, conversation flows, data enrichment

### 2. Filter Functions
Filter functions intercept and modify messages before and after they are processed by the language model. They provide powerful middleware capabilities for content moderation, logging, and request/response transformation.

- **Template**: [`templates/filter_function_template.py`](templates/filter_function_template.py)
- **Documentation**: [`docs/FILTER_FUNCTIONS.md`](docs/FILTER_FUNCTIONS.md)

**Use cases**: Content moderation, logging and analytics, adding context, response transformation, user customization

### 3. Action Functions
Action functions provide custom actions that can be triggered by the UI or other functions. They enable specific operations like file uploads, API calls, or custom workflows.

- **Template**: [`templates/action_function_template.py`](templates/action_function_template.py)
- **Documentation**: [`docs/ACTION_FUNCTIONS.md`](docs/ACTION_FUNCTIONS.md)

**Use cases**: File processing, external API calls, database operations, background tasks, user-initiated operations

## Quick Start

1. **Choose a function type** based on your use case
2. **Copy the template** from the `templates/` directory
3. **Read the documentation** in the `docs/` directory for detailed guidance
4. **Customize the template** with your specific logic
5. **Upload to OpenWebUI** via Settings > Functions
6. **Test your function** in a chat or workflow

## Template Structure

Each template includes:

- **Valves**: Configuration parameters for the function
- **UserValves**: User-specific configuration (where applicable)
- **Initialization**: Setup and metadata definition
- **Main logic**: Core functionality with detailed comments
- **Example usage**: Common patterns and use cases

## Documentation Structure

Each documentation file provides:

- **Overview**: What the function type does and when to use it
- **Structure**: Key components and how they work together
- **Common use cases**: Practical examples with code
- **Best practices**: Tips for writing robust functions
- **Testing guidance**: How to test and debug your functions
- **Troubleshooting**: Solutions to common issues

## Development Guidelines

- Keep functions focused and single-purpose
- Add proper error handling with try-except blocks
- Validate input data before processing
- Use meaningful variable names and add comments
- Test thoroughly before deploying
- Follow the patterns shown in the templates

## Contributing

Contributions are welcome! If you have examples, improvements, or new templates, please submit a pull request.

## License

MIT License - see [LICENSE](LICENSE) file for details

## Resources

- **Official Documentation**: [https://docs.openwebui.com/features/plugin/functions](https://docs.openwebui.com/features/plugin/functions)
- **OpenWebUI GitHub**: [https://github.com/open-webui/open-webui](https://github.com/open-webui/open-webui)
- **Community**: Join the OpenWebUI Discord for support and examples

## Support

For issues or questions:
1. Check the documentation in the `docs/` directory
2. Review the official OpenWebUI documentation
3. Open an issue in this repository
