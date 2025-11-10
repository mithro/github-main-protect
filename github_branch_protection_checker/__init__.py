"""GitHub Branch Protection Checker"""

from .__main__ import main
from .auth import get_github_token
from .fetcher import RepositoryFetcher
from .graphql_client import GraphQLClient
from .models import Repository

__version__ = "0.1.0"
__all__ = ["GraphQLClient", "Repository", "RepositoryFetcher", "get_github_token", "main"]
