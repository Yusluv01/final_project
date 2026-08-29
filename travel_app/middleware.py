from django.contrib.sessions.middleware import SessionMiddleware
from django.utils import timezone

from .models import Agent


# ============================================================
# AGENT ACTIVITY MIDDLEWARE
# ============================================================

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
                agent.save(
                    update_fields=[
                        'last_activity',
                        'is_online'
                    ]
                )
            except Agent.DoesNotExist:
                pass

        return response


# ============================================================
# SEPARATE ADMIN/STAFF AND CLIENT SESSIONS
# ============================================================

class PortalSessionMiddleware:
    """
    Maintain separate Django sessions for:

        Admin/Staff portal
            travelbolt_admin_session

        Client portal
            travelbolt_client_session

    Client URLs are identified by /client/.
    All other URLs use the Admin/Staff session.

    Django's official SessionMiddleware is used internally
    for both portals so normal Django session behavior is
    preserved.
    """

    ADMIN_COOKIE_NAME = 'travelbolt_admin_session'
    CLIENT_COOKIE_NAME = 'travelbolt_client_session'

    def __init__(self, get_response):

        # Create two normal Django SessionMiddleware instances.
        self.admin_session_middleware = SessionMiddleware(
            get_response
        )

        self.client_session_middleware = SessionMiddleware(
            get_response
        )

        # Give each middleware its own session cookie name.
        self.admin_session_middleware.cookie_name = (
            self.ADMIN_COOKIE_NAME
        )

        self.client_session_middleware.cookie_name = (
            self.CLIENT_COOKIE_NAME
        )

    def _is_client_request(self, request):
        """
        Client portal URLs all begin with /client/.
        """
        return request.path.startswith('/client/')

    def _get_session_middleware(self, request):
        """
        Select the correct Django SessionMiddleware instance.
        """

        if self._is_client_request(request):
            return self.client_session_middleware

        return self.admin_session_middleware

    def process_request(self, request):

        middleware = self._get_session_middleware(request)

        request.portal_session_middleware = middleware

        return middleware.process_request(request)

    def process_response(self, request, response):

        middleware = getattr(
            request,
            'portal_session_middleware',
            self.admin_session_middleware
        )

        return middleware.process_response(
            request,
            response
        )
