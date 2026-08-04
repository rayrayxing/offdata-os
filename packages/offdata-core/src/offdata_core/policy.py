"""Public approval-policy API.

The implementation lives in ``policy_typed`` so its evidence comparison helpers remain
fully type checked without suppressing argument-type validation.
"""

from .policy_typed import (
    ActionType,
    PolicyContext,
    PolicyResult,
    ProposedAction,
    evaluate_action,
)

__all__ = [
    "ActionType",
    "PolicyContext",
    "PolicyResult",
    "ProposedAction",
    "evaluate_action",
]
