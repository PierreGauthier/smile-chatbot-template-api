import logging
from domain.models import BaseContext

class ContextLogger(logging.LoggerAdapter):
    """
    Logger adapter that lets you call:
        log.info("msg", user_id=..., session_id=..., extra={...})
    and automatically merges context into `extra` so it lands in App Insights
    (customDimensions) and can also be prefixed into the message if desired.
    """

    def process(self, msg, kwargs):
        # Extract call-time context
        user_id = kwargs.pop("user_id", None)
        session_id = kwargs.pop("session_id", None)

        # Merge extras (adapter + call + context)
        merged_extra = {**(self.extra or {}), **(kwargs.pop("extra", {}) or {})}
        if user_id: 
            merged_extra["user_id"] = user_id
        if session_id: 
            merged_extra["session_id"] = session_id
        kwargs["extra"] = merged_extra

        # Build prefix for console (optional)
        prefix = " ".join(
            f"{k}={merged_extra[k]}"
            for k in ("component", "user_id", "session_id")
            if k in merged_extra
        )
        if prefix:
            msg = f"{msg} | {prefix}"
        if self.logger.level == logging.DEBUG:
            print(f"[DEBUG]: msg='{msg}', extra={merged_extra}")
        return msg, kwargs

    def debug_context(self, message:str, context:BaseContext):
        self.debug(
            message,
            user_id=context.user_id,
            session_id=context.session_id
        )

    def info_context(self, message:str, context:BaseContext):
        self.info(
            message,
            user_id=context.user_id,
            session_id=context.session_id
        )