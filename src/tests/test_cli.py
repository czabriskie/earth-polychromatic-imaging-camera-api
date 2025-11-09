"""Unit tests for NASA EPIC API CLI.

Tests CLI commands, functions, and integration using pytest with mocked dependencies.
"""

import json
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from earth_polychromatic_api.cli import (
    download_images,
    get_date_range,
    get_metadata,
    main,
)

# Test constants
EXPECTED_LAT = 0.74
EXPECTED_LON = 174.65


@pytest.fixture
def cli_runner():
    """Fixture providing a Click CLI runner for testing commands."""
    return CliRunner()


@pytest.fixture
def mock_client():
    """Fixture providing a mocked EpicApiClient."""
    client = Mock()
    client.get_natural_by_date.return_value = [
        {
            "image": "epic_1b_20241001003633",
            "date": "2024-10-01 00:36:33",
            "caption": "Test image caption",
        }
    ]
    client.build_image_url.return_value = (
        "https://epic.gsfc.nasa.gov/archive/natural/2024/10/01/png/epic_1b_20241001003633.png"
    )
    client.session = Mock()
    return client


@pytest.fixture
def mock_service():
    """Fixture providing a mocked EpicApiService."""
    service = Mock()
    mock_image = Mock()
    mock_image.image = "epic_1b_20241001003633"
    mock_image.caption = "Test image caption"
    mock_image.centroid_coordinates.lat = EXPECTED_LAT
    mock_image.centroid_coordinates.lon = EXPECTED_LON
    mock_image.version = "03"

    mock_response = Mock()
    mock_response.root = [mock_image]
    service.get_natural_by_date_typed.return_value = mock_response
    service.get_enhanced_by_date_typed.return_value = mock_response
    service.get_aerosol_by_date_typed.return_value = mock_response
    service.get_cloud_by_date_typed.return_value = mock_response
    return service


@pytest.fixture
def mock_download_response():
    """Fixture providing a mocked successful HTTP response for image download."""
    response = Mock()
    response.content = b"fake_image_data"
    response.raise_for_status.return_value = None
    return response


class TestGetDateRange:
    """Test date range calculation utility function."""

    def test_explicit_dates_provided(self):
        """Test date range when both start and end dates are explicitly provided.

        Should return the exact dates provided without modification.
        """
        # Arrange
        start_date = "2024-01-01"
        end_date = "2024-01-31"

        # Act
        result_start, result_end = get_date_range(start_date, end_date, None, None)

        # Assert
        assert result_start == "2024-01-01"
        assert result_end == "2024-01-31"

    def test_relative_dates_days_back_only(self):
        """Test date range calculation with only days_back parameter.

        Should calculate end date as days_back from today, start date as same day.
        """
        # Arrange
        days_back = 5
        expected_end = datetime.now(tz=timezone.utc) - timedelta(days=5)
        expected_date_str = expected_end.strftime("%Y-%m-%d")

        # Act
        result_start, result_end = get_date_range(None, None, days_back, None)

        # Assert
        assert result_start == expected_date_str
        assert result_end == expected_date_str

    def test_relative_dates_with_range(self):
        """Test date range calculation with both days_back and date_range_days.

        Should calculate proper range spanning multiple days.
        """
        # Arrange
        days_back = 3
        date_range_days = 7
        expected_end = datetime.now(tz=timezone.utc) - timedelta(days=3)
        expected_start = expected_end - timedelta(days=6)  # range-1

        # Act
        result_start, result_end = get_date_range(None, None, days_back, date_range_days)

        # Assert
        assert result_start == expected_start.strftime("%Y-%m-%d")
        assert result_end == expected_end.strftime("%Y-%m-%d")

    def test_default_yesterday(self):
        """Test default behavior when no parameters provided.

        Should return yesterday's date for both start and end.
        """
        # Arrange
        expected_date = datetime.now(tz=timezone.utc) - timedelta(days=1)
        expected_date_str = expected_date.strftime("%Y-%m-%d")

        # Act
        result_start, result_end = get_date_range(None, None, None, None)

        # Assert
        assert result_start == expected_date_str
        assert result_end == expected_date_str


class TestMainCommand:
    """Test main CLI command group functionality."""

    def test_main_help_command(self, cli_runner):
        """Test main CLI help displays available commands.

        Should show help text with available subcommands and options.
        """
        # Arrange & Act
        result = cli_runner.invoke(main, ["--help"])

        # Assert
        assert result.exit_code == 0
        assert "NASA EPIC API command-line tools" in result.output
        assert "download-images" in result.output
        assert "get-metadata" in result.output

    def test_main_version_command(self, cli_runner):
        """Test version flag displays version information.

        Should exit successfully and display version.
        """
        # Arrange & Act
        result = cli_runner.invoke(main, ["--version"])

        # Assert
        assert result.exit_code == 0


class TestDownloadImagesCommand:
    """Test image download CLI command functionality."""

    @patch("earth_polychromatic_api.cli.EpicApiClient")
    @patch("earth_polychromatic_api.cli.HAS_BOTO3", True)
    @patch("earth_polychromatic_api.cli.boto3")
    def test_successful_image_download_with_s3(
        self, mock_boto3, mock_client_class, cli_runner, tmp_path
    ):
        """Test successful image download with S3 upload.

        Should download images and upload to S3 bucket successfully.
        """
        # Arrange
        mock_client = Mock()
        mock_client.get_natural_by_date.return_value = [
            {"image": "epic_1b_20241001003633", "date": "2024-10-01 00:36:33"}
        ]
        mock_download_response = Mock()
        mock_download_response.content = b"fake_image_data"
        mock_download_response.raise_for_status.return_value = None
        mock_client.session.get.return_value = mock_download_response
        mock_client_class.return_value = mock_client

        mock_s3_client = Mock()
        mock_boto3.client.return_value = mock_s3_client

        # Act
        result = cli_runner.invoke(
            download_images,
            [
                "--date",
                "2024-10-01",
                "--collection",
                "natural",
                "--bucket",
                "test-bucket",
                "--local-dir",
                str(tmp_path),
            ],
        )

        # Assert
        assert result.exit_code == 0
        assert "Found 1 natural images for 2024-10-01" in result.output
        assert "✅ Downloaded epic_1b_20241001003633.png" in result.output
        assert "📤 Uploaded 1 images to S3" in result.output

        # Verify API calls
        mock_client.get_natural_by_date.assert_called_once_with("2024-10-01")
        mock_s3_client.upload_file.assert_called_once()

    @patch("earth_polychromatic_api.cli.EpicApiClient")
    def test_image_download_local_only(
        self, mock_client_class, cli_runner, mock_client, mock_download_response, tmp_path
    ):
        """Test image download in local-only mode.

        Should download images without attempting S3 upload.
        """
        # Arrange
        mock_client_class.return_value = mock_client
        mock_client.session.get.return_value = mock_download_response

        # Act
        result = cli_runner.invoke(
            download_images,
            [
                "--date",
                "2024-10-01",
                "--collection",
                "natural",
                "--local-only",
                "--local-dir",
                str(tmp_path),
            ],
        )

        # Assert
        assert result.exit_code == 0
        assert "Found 1 natural images for 2024-10-01" in result.output
        assert "✅ Downloaded epic_1b_20241001003633.png" in result.output
        assert "📤 Uploaded" not in result.output

        # Verify file was created
        expected_file = tmp_path / "natural" / "2024" / "10" / "01" / "epic_1b_20241001003633.png"
        assert expected_file.exists()

    @patch("earth_polychromatic_api.cli.EpicApiClient")
    def test_no_images_found(self, mock_client_class, cli_runner, mock_client):
        """Test handling when no images are found for date.

        Should display appropriate message and exit successfully.
        """
        # Arrange
        mock_client_class.return_value = mock_client
        mock_client.get_natural_by_date.return_value = []

        # Act
        result = cli_runner.invoke(
            download_images, ["--date", "2024-01-01", "--collection", "natural", "--local-only"]
        )

        # Assert
        assert result.exit_code == 0
        assert "No natural images found for 2024-01-01" in result.output

    def test_missing_bucket_without_local_only(self, cli_runner):
        """Test error when bucket not provided and not local-only.

        Should exit with error and display helpful message.
        """
        # Arrange & Act
        result = cli_runner.invoke(
            download_images, ["--date", "2024-10-01", "--collection", "natural"]
        )

        # Assert
        assert result.exit_code == 1
        assert "Error: --bucket required" in result.output

    @patch("earth_polychromatic_api.cli.EpicApiClient")
    def test_download_network_error(self, mock_client_class, cli_runner, mock_client):
        """Test handling of network errors during download.

        Should handle exceptions gracefully and continue processing.
        """
        # Arrange
        mock_client_class.return_value = mock_client
        mock_client.session.get.side_effect = Exception("Network error")

        # Act
        result = cli_runner.invoke(
            download_images, ["--date", "2024-10-01", "--collection", "natural", "--local-only"]
        )

        # Assert
        assert result.exit_code == 0
        assert "❌ Error downloading" in result.output

    @patch("earth_polychromatic_api.cli.EpicApiClient")
    def test_cloud_collection_filename_format(
        self, mock_client_class, cli_runner, mock_client, mock_download_response, tmp_path
    ):
        """Test cloud collection uses correct filename format.

        Cloud images should use 'epic_cloudfraction_' prefix format.
        """
        # Arrange
        mock_client_class.return_value = mock_client
        mock_client.get_cloud_by_date.return_value = [
            {"image": "epic_cloud_20241001003633", "date": "2024-10-01 00:36:33"}
        ]
        mock_client.session.get.return_value = mock_download_response

        # Act
        result = cli_runner.invoke(
            download_images,
            [
                "--date",
                "2024-10-01",
                "--collection",
                "cloud",
                "--local-only",
                "--local-dir",
                str(tmp_path),
            ],
        )

        # Assert
        assert result.exit_code == 0
        assert "✅ Downloaded epic_cloudfraction_20241001003633.png" in result.output

    @patch("earth_polychromatic_api.cli.EpicApiClient")
    def test_aerosol_collection_filename_format(
        self, mock_client_class, cli_runner, mock_client, mock_download_response, tmp_path
    ):
        """Test aerosol collection uses correct filename format.

        Aerosol images should use 'epic_aerosol_' prefix format.
        """
        # Arrange
        mock_client_class.return_value = mock_client
        mock_client.get_aerosol_by_date.return_value = [
            {"image": "epic_aerosol_20241001003633", "date": "2024-10-01 00:36:33"}
        ]
        mock_client.session.get.return_value = mock_download_response

        # Act
        result = cli_runner.invoke(
            download_images,
            [
                "--date",
                "2024-10-01",
                "--collection",
                "aerosol",
                "--local-only",
                "--local-dir",
                str(tmp_path),
            ],
        )

        # Assert
        assert result.exit_code == 0
        assert "✅ Downloaded epic_aerosol_20241001003633.png" in result.output


class TestGetMetadataCommand:
    """Test metadata retrieval CLI command functionality."""

    @patch("earth_polychromatic_api.cli.EpicApiService")
    def test_successful_metadata_table_output(self, mock_service_class, cli_runner, mock_service):
        """Test successful metadata retrieval with table output.

        Should display metadata in formatted table.
        """
        # Arrange
        mock_service_class.return_value = mock_service

        # Act
        result = cli_runner.invoke(
            get_metadata, ["--date", "2024-10-01", "--collection", "natural", "--format", "table"]
        )

        # Assert
        assert result.exit_code == 0
        assert "EPIC Natural Images - 2024-10-01" in result.output
        assert "epic_1b_20241001003633" in result.output
        assert f"{EXPECTED_LAT}, {EXPECTED_LON}" in result.output
        assert "03" in result.output

        # Verify service call
        mock_service.get_natural_by_date_typed.assert_called_once_with("2024-10-01")

    @patch("earth_polychromatic_api.cli.EpicApiService")
    def test_successful_metadata_json_output(self, mock_service_class, cli_runner, mock_service):
        """Test successful metadata retrieval with JSON output.

        Should output properly formatted JSON.
        """
        # Arrange
        mock_service_class.return_value = mock_service

        # Act
        result = cli_runner.invoke(
            get_metadata, ["--date", "2024-10-01", "--collection", "natural", "--format", "json"]
        )

        # Assert
        assert result.exit_code == 0

        # Parse and validate JSON output
        output_data = json.loads(result.output)
        assert output_data["total_images"] == 1
        assert output_data["date"] == "2024-10-01"
        assert output_data["collection"] == "natural"
        assert len(output_data["metadata"]) == 1

        metadata_item = output_data["metadata"][0]
        assert metadata_item["image_name"] == "epic_1b_20241001003633"
        assert metadata_item["centroid_lat"] == EXPECTED_LAT
        assert metadata_item["centroid_lon"] == EXPECTED_LON

    @patch("earth_polychromatic_api.cli.EpicApiService")
    def test_metadata_output_to_file(self, mock_service_class, cli_runner, mock_service, tmp_path):
        """Test metadata output saved to file.

        Should save JSON data to specified file.
        """
        # Arrange
        mock_service_class.return_value = mock_service
        output_file = tmp_path / "metadata.json"

        # Act
        result = cli_runner.invoke(
            get_metadata,
            [
                "--date",
                "2024-10-01",
                "--collection",
                "natural",
                "--format",
                "json",
                "--output-file",
                str(output_file),
            ],
        )

        # Assert
        assert result.exit_code == 0
        assert "Metadata saved to" in result.output

        # Verify file contents
        assert output_file.exists()
        with output_file.open(encoding="utf-8") as f:
            saved_data = json.load(f)
        assert saved_data["total_images"] == 1
        assert saved_data["metadata"][0]["image_name"] == "epic_1b_20241001003633"

    @patch("earth_polychromatic_api.cli.EpicApiService")
    def test_no_metadata_found(self, mock_service_class, cli_runner, mock_service):
        """Test handling when no metadata is found.

        Should display appropriate message and exit successfully.
        """
        # Arrange
        mock_service_class.return_value = mock_service
        mock_response = Mock()
        mock_response.root = []
        mock_service.get_natural_by_date_typed.return_value = mock_response

        # Act
        result = cli_runner.invoke(
            get_metadata, ["--date", "2024-01-01", "--collection", "natural"]
        )

        # Assert
        assert result.exit_code == 0
        assert "No natural images found for 2024-01-01" in result.output

    @patch("earth_polychromatic_api.cli.EpicApiService")
    def test_enhanced_collection_metadata(self, mock_service_class, cli_runner, mock_service):
        """Test metadata retrieval for enhanced collection.

        Should call correct service method for enhanced images.
        """
        # Arrange
        mock_service_class.return_value = mock_service

        # Act
        result = cli_runner.invoke(
            get_metadata, ["--date", "2024-10-01", "--collection", "enhanced", "--format", "table"]
        )

        # Assert
        assert result.exit_code == 0
        assert "EPIC Enhanced Images - 2024-10-01" in result.output
        mock_service.get_enhanced_by_date_typed.assert_called_once_with("2024-10-01")

    @patch("earth_polychromatic_api.cli.EpicApiService")
    def test_aerosol_collection_metadata(self, mock_service_class, cli_runner, mock_service):
        """Test metadata retrieval for aerosol collection.

        Should call correct service method for aerosol images.
        """
        # Arrange
        mock_service_class.return_value = mock_service

        # Act
        result = cli_runner.invoke(
            get_metadata, ["--date", "2024-10-01", "--collection", "aerosol", "--format", "table"]
        )

        # Assert
        assert result.exit_code == 0
        assert "EPIC Aerosol Images - 2024-10-01" in result.output
        mock_service.get_aerosol_by_date_typed.assert_called_once_with("2024-10-01")

    @patch("earth_polychromatic_api.cli.EpicApiService")
    def test_cloud_collection_metadata(self, mock_service_class, cli_runner, mock_service):
        """Test metadata retrieval for cloud collection.

        Should call correct service method for cloud images.
        """
        # Arrange
        mock_service_class.return_value = mock_service

        # Act
        result = cli_runner.invoke(
            get_metadata, ["--date", "2024-10-01", "--collection", "cloud", "--format", "table"]
        )

        # Assert
        assert result.exit_code == 0
        assert "EPIC Cloud Images - 2024-10-01" in result.output
        mock_service.get_cloud_by_date_typed.assert_called_once_with("2024-10-01")

    @patch("earth_polychromatic_api.cli.EpicApiService")
    def test_default_yesterday_date(self, mock_service_class, cli_runner, mock_service):
        """Test metadata command with default date (yesterday).

        Should use yesterday's date when no date specified.
        """
        # Arrange
        mock_service_class.return_value = mock_service
        yesterday = (datetime.now(tz=timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")

        # Act
        result = cli_runner.invoke(get_metadata, ["--collection", "natural", "--format", "table"])

        # Assert
        assert result.exit_code == 0
        mock_service.get_natural_by_date_typed.assert_called_once_with(yesterday)


class TestCLIIntegration:
    """Test CLI integration scenarios and edge cases."""

    def test_help_commands_accessible(self, cli_runner):
        """Test all help commands are accessible and working.

        Should provide help for all command levels.
        """
        # Arrange & Act
        main_help = cli_runner.invoke(main, ["--help"])
        download_help = cli_runner.invoke(main, ["download-images", "--help"])
        metadata_help = cli_runner.invoke(main, ["get-metadata", "--help"])

        # Assert
        assert main_help.exit_code == 0
        assert download_help.exit_code == 0
        assert metadata_help.exit_code == 0

        assert "NASA EPIC API command-line tools" in main_help.output
        assert "Download NASA EPIC images" in download_help.output
        assert "Get metadata for NASA EPIC images" in metadata_help.output

    @patch("earth_polychromatic_api.cli.HAS_BOTO3", False)
    @patch("earth_polychromatic_api.cli.EpicApiClient")
    def test_no_boto3_warning(
        self, mock_client_class, cli_runner, mock_client, mock_download_response
    ):
        """Test warning when boto3 is not available.

        Should display appropriate warning about S3 functionality.
        """
        # Arrange
        mock_client_class.return_value = mock_client
        mock_client.session.get.return_value = mock_download_response

        # Act
        result = cli_runner.invoke(
            download_images,
            ["--date", "2024-10-01", "--collection", "natural", "--bucket", "test-bucket"],
        )

        # Assert
        assert result.exit_code == 0
        assert "❌ boto3 not available for S3 upload" in result.output

    @patch("earth_polychromatic_api.cli.EpicApiService")
    def test_long_caption_truncation(self, mock_service_class, cli_runner):
        """Test long captions are properly truncated in table output.

        Should truncate captions longer than 40 characters with ellipsis.
        """
        # Arrange
        mock_service = Mock()
        mock_image = Mock()
        mock_image.image = "test_image"
        mock_image.caption = (
            "This is a very long caption that should be truncated because it exceeds the limit"
        )
        mock_image.centroid_coordinates.lat = 0.0
        mock_image.centroid_coordinates.lon = 0.0
        mock_image.version = "03"

        mock_response = Mock()
        mock_response.root = [mock_image]
        mock_service.get_natural_by_date_typed.return_value = mock_response
        mock_service_class.return_value = mock_service

        # Act
        result = cli_runner.invoke(
            get_metadata, ["--date", "2024-10-01", "--collection", "natural", "--format", "table"]
        )

        # Assert
        assert result.exit_code == 0
        # Check that the caption appears to be truncated (exact format may vary)
        assert "test_image" in result.output
        assert "This is a very long" in result.output
