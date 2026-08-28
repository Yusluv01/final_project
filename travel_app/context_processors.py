from .models import Notification


def agent_context(request):
    """Add logged-in agent information to all templates."""
    if request.user.is_authenticated:
        return {
            'agent_full_name': (
                request.user.get_full_name()
                or request.user.username
            ),
            'agent_id': getattr(
                request.user,
                'agent_id',
                'TB-0000'
            ),
        }

    return {}


def notification_context(request):
    """
    Add unread notifications and notification count
    to all authenticated agent templates.
    """
    if request.user.is_authenticated:

        notifications = (
            Notification.objects
            .filter(recipient=request.user)
            .order_by('-created_at')[:10]
        )

        unread_count = (
            Notification.objects
            .filter(
                recipient=request.user,
                is_read=False
            )
            .count()
        )

        return {
            'notifications': notifications,
            'notification_count': unread_count,
        }

    return {
        'notifications': [],
        'notification_count': 0,
    }


def system_context(request):
    """Add system information to all templates."""
    return {
        'app_name': 'Travelbolt',
        'app_version': '1.0.0',
    }
