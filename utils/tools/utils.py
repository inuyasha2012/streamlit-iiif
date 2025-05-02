def get_tool_call_arg(response, tool_index=0, arg_name=None, default=None):
    """Safely extract argument values from tool calls.

    Args:
        response: The LLM response object
        tool_index: Index of the tool call to access
        arg_name: Name of the argument to extract (if None, returns all args)
        default: Default value if extraction fails

    Returns:
        The argument value or default if not found
    """
    try:
        if not hasattr(response, 'tool_calls') or not response.tool_calls:
            return default

        tool_call = response.tool_calls[tool_index]
        if 'args' not in tool_call:
            return default

        if arg_name is None:
            return tool_call['args']

        return tool_call['args'].get(arg_name, default)
    except (IndexError, AttributeError, KeyError):
        return default