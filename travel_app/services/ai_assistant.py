# travel_app/services/ai_assistant.py
import os
import json
import logging
from django.conf import settings
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not installed. Install with: pip install openai")

class TravelAssistant:
    """AI Travel Assistant for Hajj and Umrah queries with OpenAI integration"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'OPENAI_API_KEY', None)
        self.use_openai = bool(self.api_key) and OPENAI_AVAILABLE
        
        if self.use_openai:
            openai.api_key = self.api_key
            logger.info("OpenAI API initialized successfully")
        else:
            logger.info("Using fallback knowledge base (OpenAI not available)")
        
        self.knowledge_base = self._load_knowledge_base()
        self.system_prompt = self._create_system_prompt()
    
    def _load_knowledge_base(self):
        """Load comprehensive knowledge base for Hajj and Umrah"""
        return {
            # ==================== DOCUMENTS ====================
            "documents": {
                "passport": {
                    "required": True,
                    "description": "Valid passport with at least 6 months validity from travel date",
                    "details": "Must have at least 2 blank visa pages. Passport must be valid for 6 months from the date of travel.",
                    "deadline": "Submit at least 4 weeks before travel"
                },
                "passport_photo": {
                    "required": True,
                    "description": "White background, 2x2 inches, recent (within 6 months)",
                    "details": "No glasses, no head covering (except for religious purposes). Photo must be clear and front-facing.",
                    "deadline": "Submit with application"
                },
                "visa_application": {
                    "required": True,
                    "description": "Completed visa application form",
                    "details": "Must be signed and dated. Fill out all sections accurately.",
                    "deadline": "Submit at least 4 weeks before travel"
                },
                "vaccination_certificate": {
                    "required": True,
                    "description": "Meningitis ACWY vaccination certificate",
                    "details": "Must be issued within 3 years and at least 10 days before travel. Keep original certificate.",
                    "deadline": "Submit with visa application"
                },
                "bank_statement": {
                    "required": False,
                    "description": "Proof of sufficient funds (recommended)",
                    "details": "Last 3 months of statements. Minimum balance required varies by visa type.",
                    "deadline": "Submit with application"
                },
                "travel_insurance": {
                    "required": True,
                    "description": "Travel insurance covering medical expenses",
                    "details": "Must cover at least $50,000 in medical coverage. Includes emergency evacuation.",
                    "deadline": "Submit before travel"
                },
                "flight_ticket": {
                    "required": True,
                    "description": "Confirmed round-trip flight booking",
                    "details": "Must show return flight. Direct flights recommended for Hajj/Umrah.",
                    "deadline": "Submit with application"
                },
                "hotel_booking": {
                    "required": True,
                    "description": "Confirmed hotel booking for duration of stay",
                    "details": "Must cover entire stay in Saudi Arabia. Proximity to Haram is recommended.",
                    "deadline": "Submit with application"
                },
                "mahram_letter": {
                    "required": False,
                    "description": "Letter from male guardian (for women under 45)",
                    "details": "Required for women traveling without husband/brother. Must be notarized.",
                    "deadline": "Submit with application"
                }
            },
            
            # ==================== HAJJ INFORMATION ====================
            "hajj": {
                "overview": "Hajj is the annual Islamic pilgrimage to Makkah, Saudi Arabia. It is mandatory for all physically and financially capable Muslims to perform Hajj at least once in their lifetime.",
                "timing": "Hajj takes place during the Islamic month of Dhu al-Hijjah, from the 8th to the 12th of the month.",
                "requirements": [
                    "Must be physically and financially able",
                    "Must have valid passport (6+ months validity)",
                    "Must have Hajj visa",
                    "Must have completed all vaccinations (Meningitis ACWY)",
                    "Must have travel insurance",
                    "Must have proof of accommodation in Makkah and Madinah",
                    "Must have proof of relationship for women (Mahram letter if under 45)",
                ],
                "document_checklist": [
                    "Passport (valid for 6+ months)",
                    "Hajj visa",
                    "Vaccination certificates (Meningitis ACWY)",
                    "Travel insurance (minimum $50,000 coverage)",
                    "Hotel bookings (Makkah & Madinah)",
                    "Flight tickets (round trip)",
                    "Bank statements (proof of funds)",
                    "Emergency contact information",
                    "Mahram letter (for women under 45)",
                    "Medical fitness certificate",
                ],
                "important_dates": {
                    "visa_application_deadline": "4-6 weeks before Hajj",
                    "vaccination_deadline": "At least 10 days before travel",
                    "flight_booking_deadline": "6-8 weeks before Hajj",
                    "hotel_booking_deadline": "8-10 weeks before Hajj",
                    "hajj_dates": "8th to 12th of Dhu al-Hijjah"
                },
                "rituals": [
                    "Ihram - Entering the state of pilgrimage",
                    "Tawaf - Circling the Kaaba 7 times",
                    "Sa'i - Walking between Safa and Marwah 7 times",
                    "Wuquf - Standing at Arafat",
                    "Ramy al-Jamarat - Stoning the Devil",
                    "Halq/Taqsir - Shaving/Trimming hair",
                    "Tawaf al-Ifadah - Farewell Tawaf",
                ],
                "packages": [
                    {
                        "name": "Hajj 2024 - Premium Package",
                        "price": "$8,500",
                        "star": "5-star",
                        "description": "VIP Hajj package with 5-star accommodation, private transportation, and expert guidance.",
                        "includes": [
                            "5-star hotel in Makkah (10 nights)",
                            "5-star hotel in Madinah (4 nights)",
                            "Private VIP transportation",
                            "Expert Hajj guide (English/Arabic)",
                            "All meals (breakfast, lunch, dinner)",
                            "Zamzam water package",
                            "Hajj kit (Ihram, prayer mat, etc.)",
                            "24/7 medical support",
                            "Visa processing assistance",
                            "Flight tickets (round trip)"
                        ]
                    },
                    {
                        "name": "Hajj 2024 - Standard Package",
                        "price": "$5,500",
                        "star": "4-star",
                        "description": "Comfortable Hajj package with 4-star accommodation and group transportation.",
                        "includes": [
                            "4-star hotel in Makkah (10 nights)",
                            "4-star hotel in Madinah (4 nights)",
                            "Group transportation",
                            "Hajj guide (Arabic/English)",
                            "All meals (breakfast, lunch, dinner)",
                            "Hajj kit (Ihram, prayer mat)",
                            "Medical support",
                            "Visa processing assistance",
                            "Flight tickets (round trip)"
                        ]
                    },
                    {
                        "name": "Hajj 2024 - Economy Package",
                        "price": "$3,500",
                        "star": "3-star",
                        "description": "Affordable Hajj package with 3-star accommodation for budget-conscious pilgrims.",
                        "includes": [
                            "3-star hotel in Makkah (10 nights)",
                            "3-star hotel in Madinah (4 nights)",
                            "Group transportation",
                            "Basic Hajj guidance",
                            "Meals (breakfast and dinner)",
                            "Hajj kit (Ihram)",
                            "Visa processing assistance",
                            "Flight tickets (round trip)"
                        ]
                    }
                ]
            },
            
            # ==================== UMRAH INFORMATION ====================
            "umrah": {
                "overview": "Umrah is the Islamic pilgrimage to Makkah that can be performed at any time of the year. Unlike Hajj, it is not mandatory but highly recommended.",
                "timing": "Umrah can be performed throughout the year, except during the days of Hajj.",
                "requirements": [
                    "Must have valid passport (6+ months validity)",
                    "Must have Umrah visa",
                    "Must have completed all vaccinations (Meningitis ACWY)",
                    "Must have travel insurance",
                    "Must have proof of accommodation in Makkah and Madinah",
                ],
                "document_checklist": [
                    "Passport (valid for 6+ months)",
                    "Umrah visa",
                    "Vaccination certificates (Meningitis ACWY)",
                    "Travel insurance (minimum $50,000 coverage)",
                    "Hotel bookings (Makkah & Madinah)",
                    "Flight tickets (round trip)",
                    "Bank statements (proof of funds)",
                    "Emergency contact information",
                ],
                "important_dates": {
                    "visa_application_deadline": "2-3 weeks before travel",
                    "vaccination_deadline": "At least 10 days before travel",
                    "flight_booking_deadline": "4-6 weeks before travel",
                    "hotel_booking_deadline": "6-8 weeks before travel"
                },
                "rituals": [
                    "Ihram - Entering the state of pilgrimage",
                    "Tawaf - Circling the Kaaba 7 times",
                    "Sa'i - Walking between Safa and Marwah 7 times",
                    "Halq/Taqsir - Shaving/Trimming hair",
                ],
                "packages": [
                    {
                        "name": "Umrah - Luxury Package",
                        "price": "$4,200",
                        "star": "5-star",
                        "description": "Premium Umrah experience with 5-star hotels close to Haram and VIP services.",
                        "includes": [
                            "5-star hotel in Makkah (7 nights) - Walking distance to Haram",
                            "5-star hotel in Madinah (3 nights) - Walking distance to Masjid Nabawi",
                            "Private VIP transportation",
                            "Expert Umrah guide",
                            "All meals (breakfast, lunch, dinner)",
                            "Zamzam water package",
                            "Umrah kit",
                            "24/7 concierge service",
                            "Visa processing",
                            "Flight tickets (round trip)"
                        ]
                    },
                    {
                        "name": "Umrah - Standard Package",
                        "price": "$2,800",
                        "star": "4-star",
                        "description": "Comfortable Umrah package with 4-star hotels and group services.",
                        "includes": [
                            "4-star hotel in Makkah (7 nights)",
                            "4-star hotel in Madinah (3 nights)",
                            "Group transportation",
                            "Umrah guide (Arabic/English)",
                            "All meals (breakfast, dinner)",
                            "Umrah kit",
                            "Medical support",
                            "Visa processing",
                            "Flight tickets (round trip)"
                        ]
                    },
                    {
                        "name": "Umrah - Economy Package",
                        "price": "$1,800",
                        "star": "3-star",
                        "description": "Affordable Umrah package with 3-star hotels for budget travelers.",
                        "includes": [
                            "3-star hotel in Makkah (7 nights)",
                            "3-star hotel in Madinah (3 nights)",
                            "Group transportation",
                            "Basic Umrah guidance",
                            "Meals (breakfast)",
                            "Umrah kit",
                            "Visa processing",
                            "Flight tickets (round trip)"
                        ]
                    }
                ]
            },
            
            # ==================== VISA INFORMATION ====================
            "visa": {
                "types": [
                    "Hajj Visa - For Hajj pilgrimage (specific dates)",
                    "Umrah Visa - For Umrah pilgrimage (year-round)",
                    "Tourist Visa - For tourism and leisure",
                    "Business Visa - For business purposes",
                    "Family Visit Visa - For visiting family members"
                ],
                "general_requirements": [
                    "Valid passport (6+ months validity)",
                    "Completed visa application form",
                    "Recent passport photo (white background)",
                    "Proof of accommodation in Saudi Arabia",
                    "Return flight ticket",
                    "Travel insurance (minimum $50,000 coverage)",
                    "Sufficient funds for the duration of stay",
                    "For Hajj/Umrah: Vaccination certificate (Meningitis ACWY)"
                ],
                "processing_time": "1-4 weeks depending on visa type and country of origin",
                "visa_fees": {
                    "Hajj Visa": "Varies by country and package",
                    "Umrah Visa": "Approximately $100-$150",
                    "Tourist Visa": "Approximately $80-$120",
                    "Business Visa": "Approximately $150-$250",
                    "Family Visit Visa": "Approximately $100-$150"
                }
            },
            
            # ==================== VACCINATION INFORMATION ====================
            "vaccinations": {
                "required": [
                    {
                        "name": "Meningitis ACWY",
                        "description": "Required for all travelers to Saudi Arabia for Hajj/Umrah",
                        "timing": "At least 10 days before travel",
                        "validity": "Valid for 3 years",
                        "certificate": "Required proof of vaccination"
                    }
                ],
                "recommended": [
                    {
                        "name": "Hepatitis A",
                        "description": "Recommended for all travelers",
                        "timing": "2-4 weeks before travel",
                        "validity": "Lifelong protection"
                    },
                    {
                        "name": "Typhoid",
                        "description": "Recommended for all travelers, especially those eating street food",
                        "timing": "2-4 weeks before travel",
                        "validity": "2-3 years"
                    },
                    {
                        "name": "Polio",
                        "description": "Recommended for all travelers",
                        "timing": "2-4 weeks before travel",
                        "validity": "Lifelong with boosters"
                    }
                ],
                "other_recommended": [
                    {
                        "name": "COVID-19",
                        "description": "May be required for entry",
                        "timing": "Consult with healthcare provider",
                        "validity": "Varies by vaccine type"
                    },
                    {
                        "name": "Seasonal Flu",
                        "description": "Recommended for all travelers",
                        "timing": "Annual",
                        "validity": "1 year"
                    }
                ]
            }
        }
    
    def _create_system_prompt(self):
        """Create the system prompt for OpenAI"""
        return """You are Travelbolt_AI, a professional travel assistant specializing in Hajj and Umrah travel. 
        You provide accurate, helpful, and detailed information about travel requirements, documents, visas, and vaccinations.
        
        Key information to always include:
        1. Document requirements (passport, photos, visa forms, vaccination certificates)
        2. Hajj and Umrah requirements and checklists
        3. Visa types and application process
        4. Vaccination requirements and recommendations
        5. Important dates and deadlines
        6. Hajj and Umrah packages and pricing
        
        Always be:
        - Professional and respectful
        - Accurate with information
        - Helpful and thorough
        - Friendly and welcoming
        - Culturally sensitive
        
        Format responses with clear sections using **bold headings** and bullet points.
        Always include contact information for further assistance.
        """
    
    def get_response(self, query):
        """Get AI response for user query"""
        try:
            # Try OpenAI first if available
            if self.use_openai:
                response = self._get_openai_response(query)
                if response:
                    return response
            
            # Fallback to knowledge base
            return self._get_knowledge_base_response(query)
            
        except Exception as e:
            logger.error(f"AI Assistant error: {e}")
            return self._get_knowledge_base_response(query)
    
    def _get_openai_response(self, query):
        """Get response from OpenAI API"""
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": query}
            ]
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=800,
                temperature=0.7,
                top_p=0.9,
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return None
    
    def _get_knowledge_base_response(self, query):
        """Fallback response using knowledge base"""
        query_lower = query.lower()
        
        # Package related queries
        if any(word in query_lower for word in ['package', 'packages', 'cost', 'price', 'pricing', 'how much']):
            return self._handle_package_query(query_lower)
        
        # Document related queries
        elif any(word in query_lower for word in ['document', 'passport', 'photo', 'vaccination', 'insurance', 'ticket', 'hotel', 'mahram']):
            return self._handle_document_query(query_lower)
        
        # Hajj related queries
        elif any(word in query_lower for word in ['hajj', 'pilgrimage', 'mecca', 'makkah']):
            return self._handle_hajj_query(query_lower)
        
        # Umrah related queries
        elif any(word in query_lower for word in ['umrah', 'umra', 'minor pilgrimage']):
            return self._handle_umrah_query(query_lower)
        
        # Visa related queries
        elif any(word in query_lower for word in ['visa', 'application', 'process']):
            return self._handle_visa_query(query_lower)
        
        # Vaccination related queries
        elif any(word in query_lower for word in ['vaccination', 'vaccine', 'shot', 'meningitis']):
            return self._handle_vaccination_query(query_lower)
        
        # Rituals related queries
        elif any(word in query_lower for word in ['ritual', 'tawaf', 'sa\'i', 'ihram', 'arafat']):
            return self._handle_rituals_query(query_lower)
        
        # General greeting
        elif any(word in query_lower for word in ['hi', 'hello', 'hey', 'greeting', 'assalamu', 'alaikum']):
            return self._handle_greeting()
        
        # General travel info
        else:
            return self._handle_general_query(query_lower)
    
    def _handle_package_query(self, query):
        """Handle package-related queries"""
        response = "🕋 **Hajj and Umrah Packages**\n\n"
        
        if 'hajj' in query.lower():
            response += "**Hajj Packages 2024:**\n\n"
            for pkg in self.knowledge_base['hajj']['packages']:
                response += f"**{pkg['name']}**\n"
                response += f"• Price: {pkg['price']}\n"
                response += f"• {pkg['star']} Accommodation\n"
                response += f"• {pkg['description']}\n"
                response += "• Includes:\n"
                for item in pkg['includes'][:5]:
                    response += f"  - {item}\n"
                response += "\n"
        
        if 'umrah' in query.lower() or 'umra' in query.lower():
            response += "**Umrah Packages:**\n\n"
            for pkg in self.knowledge_base['umrah']['packages']:
                response += f"**{pkg['name']}**\n"
                response += f"• Price: {pkg['price']}\n"
                response += f"• {pkg['star']} Accommodation\n"
                response += f"• {pkg['description']}\n"
                response += "• Includes:\n"
                for item in pkg['includes'][:5]:
                    response += f"  - {item}\n"
                response += "\n"
        
        if 'cheap' in query.lower() or 'budget' in query.lower():
            response += "**Budget Options:**\n"
            response += "• Hajj Economy Package: $3,500\n"
            response += "• Umrah Economy Package: $1,800\n"
        
        return response
    
    def _handle_rituals_query(self, query):
        """Handle rituals-related queries"""
        response = "🕋 **Hajj and Umrah Rituals**\n\n"
        
        if 'hajj' in query.lower():
            response += "**Hajj Rituals (Step by Step):**\n\n"
            for i, ritual in enumerate(self.knowledge_base['hajj']['rituals'], 1):
                response += f"{i}. {ritual}\n"
        
        if 'umrah' in query.lower() or 'umra' in query.lower():
            response += "**Umrah Rituals (Step by Step):**\n\n"
            for i, ritual in enumerate(self.knowledge_base['umrah']['rituals'], 1):
                response += f"{i}. {ritual}\n"
        
        if 'ihram' in query.lower():
            response += "\n**Ihram Guidelines:**\n"
            response += "• Enter the state of Ihram before crossing the Miqat\n"
            response += "• Men: Wear two white unstitched cloths\n"
            response += "• Women: Wear modest Islamic clothing\n"
            response += "• Avoid: Perfume, cutting hair/nails, sexual activity, hunting\n"
        
        return response
    
    def _handle_document_query(self, query):
        """Handle document-related queries"""
        response = "📋 **Required Documents for Hajj/Umrah Travel**\n\n"
        
        # Check which documents are being asked about
        if 'passport' in query:
            doc = self.knowledge_base['documents']['passport']
            response += f"**Passport Requirements:**\n"
            response += f"• {doc['description']}\n"
            response += f"• {doc['details']}\n"
            response += f"• Deadline: {doc['deadline']}\n\n"
        
        if 'photo' in query:
            doc = self.knowledge_base['documents']['passport_photo']
            response += f"**Passport Photo Requirements:**\n"
            response += f"• {doc['description']}\n"
            response += f"• {doc['details']}\n"
            response += f"• Deadline: {doc['deadline']}\n\n"
        
        if 'visa' in query:
            doc = self.knowledge_base['documents']['visa_application']
            response += f"**Visa Application:**\n"
            response += f"• {doc['description']}\n"
            response += f"• {doc['details']}\n"
            response += f"• Deadline: {doc['deadline']}\n\n"
        
        if 'vaccination' in query or 'vaccine' in query:
            doc = self.knowledge_base['documents']['vaccination_certificate']
            response += f"**Vaccination Certificate:**\n"
            response += f"• {doc['description']}\n"
            response += f"• {doc['details']}\n"
            response += f"• Deadline: {doc['deadline']}\n\n"
        
        if 'insurance' in query:
            doc = self.knowledge_base['documents']['travel_insurance']
            response += f"**Travel Insurance:**\n"
            response += f"• {doc['description']}\n"
            response += f"• {doc['details']}\n"
            response += f"• Deadline: {doc['deadline']}\n\n"
        
        if 'ticket' in query or 'flight' in query:
            doc = self.knowledge_base['documents']['flight_ticket']
            response += f"**Flight Ticket:**\n"
            response += f"• {doc['description']}\n"
            response += f"• {doc['details']}\n"
            response += f"• Deadline: {doc['deadline']}\n\n"
        
        if 'hotel' in query:
            doc = self.knowledge_base['documents']['hotel_booking']
            response += f"**Hotel Booking:**\n"
            response += f"• {doc['description']}\n"
            response += f"• {doc['details']}\n"
            response += f"• Deadline: {doc['deadline']}\n\n"
        
        if 'mahram' in query:
            doc = self.knowledge_base['documents']['mahram_letter']
            response += f"**Mahram Letter:**\n"
            response += f"• {doc['description']}\n"
            response += f"• {doc['details']}\n"
            response += f"• Deadline: {doc['deadline']}\n\n"
        
        # If no specific document was matched
        if "passport" not in query and "photo" not in query and "visa" not in query and \
           "vaccination" not in query and "insurance" not in query and "ticket" not in query and \
           "flight" not in query and "hotel" not in query and "mahram" not in query:
            
            response = "📋 **Complete Document Checklist for Hajj/Umrah:**\n\n"
            for doc_name, doc_info in self.knowledge_base['documents'].items():
                required = "✅" if doc_info['required'] else "⚠️"
                response += f"{required} **{doc_name.replace('_', ' ').title()}**\n"
                response += f"   {doc_info['description']}\n"
                response += f"   Deadline: {doc_info['deadline']}\n\n"
        
        response += "\n**For more details on specific packages, ask me about 'hajj packages' or 'umrah packages'.**"
        return response
    
    def _handle_hajj_query(self, query):
        """Handle Hajj-related queries"""
        hajj_info = self.knowledge_base['hajj']
        
        response = "🕋 **Hajj Information**\n\n"
        
        if 'overview' in query or 'what is' in query or 'about' in query:
            response += f"**Overview:**\n{hajj_info['overview']}\n\n"
            response += f"**Timing:** {hajj_info['timing']}\n\n"
        
        if 'requirement' in query or 'need' in query or 'must' in query:
            response += "**Requirements for Hajj:**\n"
            for req in hajj_info['requirements']:
                response += f"• {req}\n"
            response += "\n"
        
        if 'document' in query or 'checklist' in query:
            response += "**Document Checklist for Hajj:**\n"
            for doc in hajj_info['document_checklist']:
                response += f"• {doc}\n"
            response += "\n"
        
        if 'date' in query or 'deadline' in query or 'when' in query:
            response += "**Important Dates for Hajj:**\n"
            for key, value in hajj_info['important_dates'].items():
                response += f"• {key.replace('_', ' ').title()}: {value}\n"
            response += "\n"
        
        if 'ritual' in query or 'step' in query:
            response += "**Hajj Rituals (Step by Step):**\n"
            for i, ritual in enumerate(hajj_info['rituals'], 1):
                response += f"{i}. {ritual}\n"
            response += "\n"
        
        if 'package' in query or 'cost' in query or 'price' in query:
            response += "**Hajj Packages:**\n\n"
            for pkg in hajj_info['packages']:
                response += f"**{pkg['name']}** - {pkg['price']}\n"
                response += f"• {pkg['star']}\n"
                response += f"• {pkg['description']}\n"
                response += f"• Includes: {', '.join(pkg['includes'][:3])}...\n\n"
        
        # If no specific aspect was asked
        if 'overview' not in query and 'requirement' not in query and 'document' not in query and \
           'checklist' not in query and 'date' not in query and 'deadline' not in query and \
           'ritual' not in query and 'package' not in query and 'cost' not in query:
            response += "**Hajj Overview:**\n"
            response += f"{hajj_info['overview']}\n\n"
            response += f"**Timing:** {hajj_info['timing']}\n\n"
            response += "**Key Requirements:**\n"
            for req in hajj_info['requirements'][:3]:
                response += f"• {req}\n"
            response += "\n**For a complete checklist and deadlines, ask me about 'hajj documents' or 'hajj deadlines'.**"
        
        return response
    
    def _handle_umrah_query(self, query):
        """Handle Umrah-related queries"""
        umrah_info = self.knowledge_base['umrah']
        
        response = "🕋 **Umrah Information**\n\n"
        
        if 'overview' in query or 'what is' in query or 'about' in query:
            response += f"**Overview:**\n{umrah_info['overview']}\n\n"
            response += f"**Timing:** {umrah_info['timing']}\n\n"
        
        if 'requirement' in query or 'need' in query or 'must' in query:
            response += "**Requirements for Umrah:**\n"
            for req in umrah_info['requirements']:
                response += f"• {req}\n"
            response += "\n"
        
        if 'document' in query or 'checklist' in query:
            response += "**Document Checklist for Umrah:**\n"
            for doc in umrah_info['document_checklist']:
                response += f"• {doc}\n"
            response += "\n"
        
        if 'date' in query or 'deadline' in query or 'when' in query:
            response += "**Important Dates for Umrah:**\n"
            for key, value in umrah_info['important_dates'].items():
                response += f"• {key.replace('_', ' ').title()}: {value}\n"
            response += "\n"
        
        if 'ritual' in query or 'step' in query:
            response += "**Umrah Rituals (Step by Step):**\n"
            for i, ritual in enumerate(umrah_info['rituals'], 1):
                response += f"{i}. {ritual}\n"
            response += "\n"
        
        if 'package' in query or 'cost' in query or 'price' in query:
            response += "**Umrah Packages:**\n\n"
            for pkg in umrah_info['packages']:
                response += f"**{pkg['name']}** - {pkg['price']}\n"
                response += f"• {pkg['star']}\n"
                response += f"• {pkg['description']}\n"
                response += f"• Includes: {', '.join(pkg['includes'][:3])}...\n\n"
        
        # If no specific aspect was asked
        if 'overview' not in query and 'requirement' not in query and 'document' not in query and \
           'checklist' not in query and 'date' not in query and 'deadline' not in query and \
           'ritual' not in query and 'package' not in query and 'cost' not in query:
            response += "**Umrah Overview:**\n"
            response += f"{umrah_info['overview']}\n\n"
            response += f"**Timing:** {umrah_info['timing']}\n\n"
            response += "**Key Requirements:**\n"
            for req in umrah_info['requirements'][:3]:
                response += f"• {req}\n"
            response += "\n**For a complete checklist and deadlines, ask me about 'umrah documents' or 'umrah deadlines'.**"
        
        return response
    
    def _handle_visa_query(self, query):
        """Handle visa-related queries"""
        visa_info = self.knowledge_base['visa']
        
        response = "🛂 **Visa Information**\n\n"
        
        if 'type' in query or 'kind' in query:
            response += "**Types of Visas:**\n"
            for visa_type in visa_info['types']:
                response += f"• {visa_type}\n"
            response += "\n"
        
        if 'requirement' in query or 'need' in query:
            response += "**General Visa Requirements:**\n"
            for req in visa_info['general_requirements']:
                response += f"• {req}\n"
            response += "\n"
        
        if 'time' in query or 'process' in query or 'how long' in query:
            response += f"**Processing Time:** {visa_info['processing_time']}\n\n"
        
        if 'fee' in query or 'cost' in query:
            response += "**Visa Fees (Approximate):**\n"
            for visa_type, fee in visa_info['visa_fees'].items():
                response += f"• {visa_type}: {fee}\n"
            response += "\n"
        
        # If no specific aspect was asked
        if 'type' not in query and 'requirement' not in query and 'need' not in query and \
           'time' not in query and 'process' not in query and 'fee' not in query and 'cost' not in query:
            response += "**Visa Overview:**\n"
            response += "A visa is required for all travelers to Saudi Arabia. "
            response += "The type of visa depends on the purpose of your travel.\n\n"
            response += f"**Processing Time:** {visa_info['processing_time']}\n\n"
            response += "**Common Visa Types:**\n"
            for visa_type in visa_info['types'][:3]:
                response += f"• {visa_type}\n"
            response += "\n**For more details, ask me about 'visa requirements' or 'visa processing time'.**"
        
        return response
    
    def _handle_vaccination_query(self, query):
        """Handle vaccination-related queries"""
        vac_info = self.knowledge_base['vaccinations']
        
        response = "💉 **Vaccination Information**\n\n"
        
        if 'required' in query or 'must' in query or 'need' in query:
            response += "**Required Vaccinations:**\n"
            for vac in vac_info['required']:
                response += f"• **{vac['name']}**\n"
                response += f"  {vac['description']}\n"
                response += f"  Timing: {vac['timing']}\n"
                response += f"  Validity: {vac['validity']}\n"
                response += f"  Certificate: {vac.get('certificate', 'Required')}\n\n"
        
        if 'recommended' in query:
            response += "**Recommended Vaccinations:**\n"
            for vac in vac_info['recommended']:
                response += f"• **{vac['name']}**\n"
                response += f"  {vac['description']}\n"
                response += f"  Timing: {vac['timing']}\n"
                response += f"  Validity: {vac['validity']}\n\n"
        
        if 'other' in query or 'additional' in query:
            if 'other_recommended' in vac_info:
                response += "**Other Recommended Vaccinations:**\n"
                for vac in vac_info['other_recommended']:
                    response += f"• **{vac['name']}**\n"
                    response += f"  {vac['description']}\n"
                    response += f"  Timing: {vac['timing']}\n\n"
        
        # If no specific aspect was asked
        if 'required' not in query and 'recommended' not in query and 'other' not in query and 'additional' not in query:
            response += "**Vaccination Overview:**\n"
            response += "Certain vaccinations are required and recommended for travel to Saudi Arabia.\n\n"
            response += "**Required:**\n"
            for vac in vac_info['required']:
                response += f"• {vac['name']} - {vac['description']}\n"
            response += "\n**Recommended:**\n"
            for vac in vac_info['recommended'][:2]:
                response += f"• {vac['name']} - {vac['description']}\n"
            response += "\n**For detailed information, ask me about 'required vaccinations' or 'recommended vaccinations'.**"
        
        return response
    
    def _handle_greeting(self):
        """Handle greeting"""
        return """👋 **Assalamu Alaikum! Welcome to Travelbolt_AI Travel Assistant!**

I'm here to help you with all your Hajj and Umrah travel needs. Here's what I can assist you with:

**Documents:**
• Passport requirements and validity
• Visa application process
• Vaccination certificates
• Travel insurance
• Hotel and flight bookings

🕋 **Hajj & Umrah:**
• Requirements and eligibility
• Document checklists
• Important dates and deadlines
• Step-by-step rituals guides
• Package options and pricing

 **Visa:**
• Types of visas (Hajj, Umrah, Tourist, Business, Family)
• Requirements and processing time
• Visa fees

**Vaccinations:**
• Required and recommended vaccines
• Timing and validity

**Just ask me a question and I'll help you!**

Example questions:
• "What documents do I need for Hajj?"
• "What vaccinations are required for Umrah?"
• "How do I apply for a visa?"
• "What are the Hajj packages available?"
• "What is the deadline for visa applications?"
• "Tell me about Umrah rituals"
"""
    
    def _handle_general_query(self, query):
        """Handle general travel queries"""
        response = "🤔 **I'm not sure I fully understand your question.**\n\n"
        response += "Here are some topics I can help you with:\n\n"
        response += "📋 **Documents:**\n"
        response += "• Passport, photos, visa forms\n"
        response += "• Vaccination certificates\n"
        response += "• Travel insurance, flight tickets\n\n"
        response += "🕋 **Hajj & Umrah:**\n"
        response += "• Requirements and eligibility\n"
        response += "• Document checklists\n"
        response += "• Important dates and deadlines\n"
        response += "• Rituals and step-by-step guides\n"
        response += "• Package options and pricing\n\n"
        response += " **Visa:**\n"
        response += "• Types of visas\n"
        response += "• Requirements and processing\n"
        response += "• Visa fees\n\n"
        response += "💉 **Vaccinations:**\n"
        response += "• Required and recommended vaccines\n"
        response += "• Timing and validity\n\n"
        response += "**Please ask me a specific question like:**\n"
        response += "• 'What documents do I need for Hajj?'\n"
        response += "• 'What vaccinations are required for Umrah?'\n"
        response += "• 'How do I apply for a visa?'\n"
        response += "• 'What are the Hajj packages available?'\n"
        response += "• 'Tell me about Umrah rituals'"
        
        return response


# Create a single instance for reuse
ai_assistant = TravelAssistant()