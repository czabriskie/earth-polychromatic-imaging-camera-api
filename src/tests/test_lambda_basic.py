"""Basic unit tests for AWS Lambda handler integration.

Tests the main Lambda handler function with mocked CLI calls.
"""

from unittest.mock import Mock, patch

import pytest

from lambda_handler import handler as lambda_handler


@pytest.fixture
def lambda_context():
    """Fixture providing a mocked Lambda context object."""
    context = Mock()
    context.function_name = "test-epic-downloader"
    context.function_version = "$LATEST"
    context.aws_request_id = "test-request-123"
    context.get_remaining_time_in_millis = Mock(return_value=60000)
    return context


class TestBasicLambdaHandler:
    """Test basic Lambda handler functionality."""

    @patch("lambda_handler.execute_downloads")
    def test_successful_lambda_execution(self, mock_execute_downloads, lambda_context):
        """Test successful Lambda execution with valid event."""
        # Arrange
        event = {"bucket": "test-bucket"}
        mock_execute_downloads.return_value = (5, 5, "epic-images --bucket test-bucket")

        # Act
        result = lambda_handler(event, lambda_context)

        # Assert
        assert result["statusCode"] == 200
        assert result["success"] is True
        assert "details" in result
        assert result["details"]["images_downloaded"] == 5
        assert result["details"]["images_uploaded"] == 5

    def test_lambda_missing_bucket(self, lambda_context):
        """Test Lambda execution fails without required bucket parameter."""
        # Arrange
        event = {}

        # Act
        result = lambda_handler(event, lambda_context)

        # Assert
        assert result["statusCode"] == 500
        assert result["success"] is False
        assert "error" in result

    @patch("lambda_handler.execute_downloads")
    def test_lambda_execution_error(self, mock_execute_downloads, lambda_context):
        """Test Lambda handles execution errors gracefully."""
        # Arrange
        event = {"bucket": "test-bucket"}
        mock_execute_downloads.side_effect = Exception("Download failed")

        # Act
        result = lambda_handler(event, lambda_context)

        # Assert
        assert result["statusCode"] == 500
        assert result["success"] is False
        assert "error" in result
        assert "details" in result
        assert result["details"]["error_type"] == "Exception"
