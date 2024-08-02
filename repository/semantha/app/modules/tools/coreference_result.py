from langchain_core.tools import tool

@tool
def coreference_result(coreference_result: str):
    """Full coreferenced text result of coreference resolution."""

    return text