"""GitHub Branch Protection Checker"""
from .auth import get_github_token
from .graphql_client import GraphQLClient
from .fetcher import RepositoryFetcher
from .models import Repository
from .__main__ import main

__version__ = "0.1.0"
__all__ = ['get_github_token', 'GraphQLClient', 'RepositoryFetcher', 'Repository', 'main']
