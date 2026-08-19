from .models import Notification

def agent_context(request):
    """Add agent information to all templates"""
    if request.user.is_authenticated:
        return {
            'agent_full_name': request.user.get_full_name() or request.user.username,
            'agent_id': getattr(request.user, 'agent_id', 'TB-0000'),
        }
    return {}

def notification_context(request):
    """Add notification count to all templates"""
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        return {
            'notification_count': unread_count,
        }
    return {'notification_count': 0}

def system_context(request):
    """Add system information to all templates"""
    return {
        'app_name': 'Travelbolt_AI',
        'app_version': '1.0.0',
    }