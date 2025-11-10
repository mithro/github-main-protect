from unittest.mock import MagicMock, patch

import requests

from github_branch_protection_checker.graphql_client import GraphQLClient


def test_graphql_client_successful_query():
    """Test successful GraphQL query execution"""
    client = GraphQLClient("test_token")

    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"viewer": {"login": "testuser"}}}
        mock_post.return_value = mock_response

        result = client.execute("query { viewer { login } }")

        assert result == {"viewer": {"login": "testuser"}}
        mock_post.assert_called_once_with(
            "https://api.github.com/graphql",
            json={"query": "query { viewer { login } }"},
            headers={"Authorization": "Bearer test_token", "Content-Type": "application/json"},
            timeout=30,
        )


def test_graphql_client_with_variables():
    """Test GraphQL query with variables"""
    client = GraphQLClient("test_token")

    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"result": "ok"}}
        mock_post.return_value = mock_response

        result = client.execute(
            "query($var: String) { test(input: $var) }", variables={"var": "value"}
        )

        assert result == {"result": "ok"}
        call_args = mock_post.call_args
        assert call_args[1]["json"]["variables"] == {"var": "value"}


def test_graphql_client_http_error():
    """Test handling of HTTP errors"""
    client = GraphQLClient("test_token")

    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response

        try:
            client.execute("query { viewer { login } }")
            raise AssertionError("Should have raised RuntimeError")
        except RuntimeError as e:
            assert "401" in str(e)
            assert "Unauthorized" in str(e)


def test_graphql_client_graphql_errors():
    """Test handling of GraphQL errors in response"""
    client = GraphQLClient("test_token")

    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "errors": [{"message": "Field not found"}, {"message": "Another error"}]
        }
        mock_post.return_value = mock_response

        try:
            client.execute("query { invalid }")
            raise AssertionError("Should have raised RuntimeError")
        except RuntimeError as e:
            assert "GraphQL error" in str(e)
            assert "Field not found" in str(e)


def test_graphql_client_network_error():
    """Test handling of network errors"""
    client = GraphQLClient("test_token")

    with patch("requests.post") as mock_post:
        mock_post.side_effect = requests.ConnectionError("Network unreachable")

        try:
            client.execute("query { viewer { login } }")
            raise AssertionError("Should have raised RuntimeError")
        except RuntimeError as e:
            assert "Failed to connect" in str(e)
            assert "Network unreachable" in str(e)
