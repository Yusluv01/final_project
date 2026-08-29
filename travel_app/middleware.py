from importlib import import_module

from django.conf import settings
from django.utils import timezone
from django.utils.cache import patch_vary_headers
from django.utils.http import http_date

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
    """

    ADMIN_COOKIE_NAME = 'travelbolt_admin_session'
    CLIENT_COOKIE_NAME = 'travelbolt_client_session'

    def __init__(self, get_response):
        self.get_response = get_response

        engine = import_module(settings.SESSION_ENGINE)
        self.SessionStore = engine.SessionStore

    def _is_client_request(self, request):
        return request.path.startswith('/client/')

    def _get_cookie_name(self, request):
        if self._is_client_request(request):
            return self.CLIENT_COOKIE_NAME

        return self.ADMIN_COOKIE_NAME

    def process_request(self, request):
        cookie_name = self._get_cookie_name(request)

        session_key = request.COOKIES.get(cookie_name)

        request.portal_session_cookie_name = cookie_name

        if session_key:
            request.session = self.SessionStore(
                session_key=session_key
            )
        else:
            request.session = self.SessionStore()

    def process_response(self, request, response):

        if not hasattr(request, 'session'):
            return response

        try:
            accessed = request.session.accessed
            modified = request.session.modified
            empty = request.session.is_empty()
        except AttributeError:
            return response

        cookie_name = getattr(
            request,
            'portal_session_cookie_name',
            self.ADMIN_COOKIE_NAME
        )

        if accessed:
            patch_vary_headers(
                response,
                ('Cookie',)
            )

        # ----------------------------------------------------
        # SESSION WAS DELETED
        # ----------------------------------------------------

        if empty:

            if response.status_code != 500:

                response.delete_cookie(
                    cookie_name,
                    path=settings.SESSION_COOKIE_PATH,
                    domain=settings.SESSION_COOKIE_DOMAIN,
                    samesite=settings.SESSION_COOKIE_SAMESITE,
                )

            return response

        # ----------------------------------------------------
        # SESSION NEEDS TO BE SAVED
        # ----------------------------------------------------

        if (
            modified
            or settings.SESSION_SAVE_EVERY_REQUEST
        ):

            if request.session.session_key is None:
                request.session.save()

            max_age = request.session.get_expiry_age()

            if request.session.get_expire_at_browser_close():
                expires = None
                max_age = None
            else:
                expires = http_date(
                    timezone.now().timestamp()
                    + max_age
                )

            response.set_cookie(
                cookie_name,
                request.session.session_key,
                max_age=max_age,
                expires=expires,
                domain=settings.SESSION_COOKIE_DOMAIN,
                path=settings.SESSION_COOKIE_PATH,
                secure=settings.SESSION_COOKIE_SECURE,
                httponly=settings.SESSION_COOKIE_HTTPONLY,
                samesite=settings.SESSION_COOKIE_SAMESITE,
            )

        return response
