"""Data models for repository information"""
from typing import Dict, Any, Optional
from dataclasses import dataclass


def is_protected(branch_ref: Dict[str, Any]) -> bool:
    """
    Check if a branch has any protection enabled.

    A branch is protected if ANY of these are true:
    - branchProtectionRule is not null (old system)
    - refUpdateRule is not null (old system, non-admin view)
    - rules.totalCount > 0 (new ruleset system)

    Args:
        branch_ref: GraphQL defaultBranchRef data

    Returns:
        True if branch has any protection, False otherwise
    """
    if branch_ref.get('branchProtectionRule') is not None:
        return True
    if branch_ref.get('refUpdateRule') is not None:
        return True
    if branch_ref.get('rules', {}).get('totalCount', 0) > 0:
        return True
    return False


@dataclass
class Repository:
    """Repository information from GitHub"""

    name: str
    owner: str
    url: str
    default_branch: Optional[str]
    is_private: bool
    is_fork: bool
    is_archived: bool
    has_protection: bool

    @classmethod
    def from_graphql(cls, data: Dict[str, Any]) -> 'Repository':
        """
        Create Repository from GraphQL response data.

        Args:
            data: Repository node from GraphQL response

        Returns:
            Repository instance
        """
        default_branch_ref = data.get('defaultBranchRef')

        return cls(
            name=data['name'],
            owner=data['owner']['login'],
            url=data['url'],
            default_branch=default_branch_ref['name'] if default_branch_ref else None,
            is_private=data['isPrivate'],
            is_fork=data['isFork'],
            is_archived=data['isArchived'],
            has_protection=is_protected(default_branch_ref) if default_branch_ref else False
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert repository to dictionary for export.

        Returns:
            Dictionary with repository information
        """
        return {
            'name': self.name,
            'owner': self.owner,
            'url': self.url,
            'default_branch': self.default_branch,
            'is_private': self.is_private,
            'is_fork': self.is_fork
        }
