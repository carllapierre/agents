from langchain_core.tools import tool

@tool
def chunks(array_of_chunks: list):
    """List of chunks split for maximum semantic relevance efficiency."""

    return array_of_chunks