"""off/data venture Hermes plugin bootstrap.

The Hermes plugin API moves quickly. START_HERE requires validating this adapter
against the pinned Hermes release before enablement. Pure policy functions live
in tools.py so they can be tested independently of Hermes.
"""
from . import tools


def register(ctx):
    """Register deterministic tools using the pinned Hermes plugin context.

    This intentionally fails closed if the expected API is unavailable rather
    than silently pretending the plugin is active.
    """
    if not hasattr(ctx, "register_tool"):
        raise RuntimeError("Pinned Hermes plugin API lacks register_tool; adapt and independently test before enabling")
    exported = {
        "g3_direct_admissibility": tools.g3_direct_admissibility,
        "normalize_operation_fingerprint": tools.normalize_operation_fingerprint,
        "classify_concern_action": tools.classify_concern_action,
        "authority_precheck": tools.authority_precheck,
    }
    for name, fn in exported.items():
        ctx.register_tool(name, fn)
