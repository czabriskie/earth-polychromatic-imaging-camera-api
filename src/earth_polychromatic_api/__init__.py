"""Earth Polychromatic API Package.

A Python client for NASA's Earth Polychromatic Imaging Camera (EPIC) API.
"""

from .client import EpicApiClient
from .service import EpicApiService
from .models import (
    EpicImageMetadata,
    NaturalImageMetadata,
    EnhancedImageMetadata,
    AerosolImageMetadata,
    CloudImageMetadata,
    NaturalImagesResponse,
    EnhancedImagesResponse,
    AerosolImagesResponse,
    CloudImagesResponse,
    AvailableDatesResponse,
    AvailableDate,
    Coordinates2D,
    Position3D,
    AttitudeQuaternions,
    ImageryCoordinates,
)

__version__ = "1.0.0"
__all__ = [
    "AerosolImageMetadata",
    "AerosolImagesResponse",
    "AttitudeQuaternions",
    "AvailableDate",
    "AvailableDatesResponse",
    "CloudImageMetadata",
    "CloudImagesResponse",
    "Coordinates2D",
    "EnhancedImageMetadata",
    "EnhancedImagesResponse",
    "EpicApiClient",
    "EpicApiService",
    "EpicImageMetadata",
    "ImageryCoordinates",
    "NaturalImageMetadata",
    "NaturalImagesResponse",
    "Position3D",
]
