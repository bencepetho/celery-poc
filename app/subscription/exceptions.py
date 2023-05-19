class SubscriptionError(Exception):
    """Base class for subscription API errors."""


class WebhookError(SubscriptionError):
    """Webhook related subscription API error."""
