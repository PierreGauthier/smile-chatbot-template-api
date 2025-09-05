import logging
from models import SearchContext

class ContextLogger(logging.LoggerAdapter):
    """
    Logger adapter that lets you call:
        log.info("msg", user_id=..., session_id=..., extra={...})
    and automatically merges context into `extra` so it lands in App Insights
    (customDimensions) and can also be prefixed into the message if desired.
    """
    def process(self, msg, kwargs):
        # Pull call-time context
        user_id = kwargs.pop("user_id", None)
        session_id = kwargs.pop("session_id", None)

        # Merge any existing extra with adapter's extra
        call_extra = kwargs.pop("extra", {}) or {}
        merged_extra = {**(self.extra or {}), **call_extra}
        if user_id is not None:
            merged_extra["user_id"] = user_id
        if session_id is not None:
            merged_extra["session_id"] = session_id

        # Put back as the official logging 'extra'
        kwargs["extra"] = merged_extra

        # (Optional) also prefix the message for nicer console output
        prefix_bits = []
        if "component" in merged_extra: prefix_bits.append(f"component={merged_extra['component']}")
        if user_id is not None: prefix_bits.append(f"user_id={user_id}")
        if session_id is not None: prefix_bits.append(f"session_id={session_id}")
        prefix = " ".join(prefix_bits)
        if prefix:
            msg = f"{msg} | {prefix}"

        return msg, kwargs

    def debug_context(self, message:str, context:SearchContext):
        self.debug(
            message,
            user_id=context.user_id,
            session_id=context.session_id
        )