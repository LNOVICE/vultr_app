"""Vultr CLI - A Python CLI and mobile application for Vultr cloud services."""

__version__ = "0.1.0"
__author__ = "LNOVICE"
__email__ = "your.email@example.com"
__description__ = "A CLI and mobile application for Vultr cloud services"

from .api.client import VultrAPI
from .ui.app import VultrCliApp

__all__ = ["VultrAPI", "VultrCliApp"]