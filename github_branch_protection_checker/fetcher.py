"""Repository fetcher with pagination support"""
from typing import List, Optional
from .graphql_client import GraphQLClient
from .models import Repository


REPO_QUERY = """
query($cursor: String) {
  viewer {
    repositories(first: 100, after: $cursor, ownerAffiliations: OWNER) {
      pageInfo {
        hasNextPage
        endCursor
      }
      nodes {
        name
        url
        defaultBranchRef {
          name
          branchProtectionRule {
            id
          }
          refUpdateRule {
            id
          }
          rules(first: 1) {
            totalCount
          }
        }
        owner {
          login
        }
        isPrivate
        isFork
        isArchived
      }
    }
  }
}
"""


class RepositoryFetcher:
    """Fetches repositories from GitHub with pagination"""

    def __init__(self, client: GraphQLClient):
        """
        Initialize repository fetcher.

        Args:
            client: GraphQL client instance
        """
        self.client = client

    def fetch_all_repositories(self) -> List[Repository]:
        """
        Fetch all repositories owned by the authenticated user.

        Handles pagination automatically, fetching 100 repos per request.

        Returns:
            List of Repository instances
        """
        repositories = []
        cursor: Optional[str] = None
        has_next_page = True

        while has_next_page:
            variables = {'cursor': cursor}
            data = self.client.execute(REPO_QUERY, variables=variables)

            repo_data = data['viewer']['repositories']
            page_info = repo_data['pageInfo']

            for node in repo_data['nodes']:
                repo = Repository.from_graphql(node)
                repositories.append(repo)

            has_next_page = page_info['hasNextPage']
            cursor = page_info['endCursor']

        return repositories
