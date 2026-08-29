from django.utils import timezone
from .models import Agent


class AgentActivityMiddleware:
    """Track agent activity"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            try:
                agent = Agent.objects.get(id=request.user.id)
                agent.last_activity = timezone.now()
                agent.is_online = True
                agent.save(update_fields=['last_activity', 'is_online'])
            except Agent.DoesNotExist:
                pass

        return response
