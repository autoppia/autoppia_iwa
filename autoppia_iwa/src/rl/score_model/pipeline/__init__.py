"""
Score-model pipeline utilities.

This package now groups the data-preparation, training, and evaluation phases
used to build the reward model dataset, providing a single point of
coordination for paths and shared helpers.
"""

from . import paths, phases
from .data_preparation import *  # noqa: F403

__all__ = ["paths", "phases"]
