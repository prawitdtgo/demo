import os


def get_local_scope(scope: str) -> str:
    """Get a local scope.

    :param scope: Scope
    :return: Local scope
    """
    return f"api://{os.getenv('AZURE_AUDIENCE')}/{scope}"


def get_microsoft_graph_scope(scope: str) -> str:
    """Get a Microsoft Graph scope.

    :param scope: Scope
    :return: Microsoft Graph scope
    """
    return f"https://graph.microsoft.com/{scope}"
