"""
Become - A lazy evaluation library for Python with context-aware callable wrappers.

This package provides a simple and elegant way to implement lazy evaluation
and dependency injection patterns in Python applications.

The core concept revolves around 'Be' objects that lazily evaluate their values
only when needed, storing results in a context dictionary for efficient reuse.
"""
from .cell import Cell, cell
from .slot import BaseSlot, Slot, slot
from .types import LazilyCallable


__version__ = "0.6.0"
__all__ = ["BaseSlot", "Cell", "LazilyCallable", "Slot", "cell", "slot"]
