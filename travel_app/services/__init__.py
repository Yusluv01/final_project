from .ai_assistant import TravelAssistant, ai_assistant

# Try to import LetsFG service, but don't fail if it doesn't exist
try:
    from .letsfg_service import LetsFGService
    letsfg_service = LetsFGService()
except ImportError:
    LetsFGService = None
    letsfg_service = None

__all__ = ['TravelAssistant', 'ai_assistant', 'LetsFGService', 'letsfg_service']