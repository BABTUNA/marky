"""
Content extractor module.
Extracts services, pricing, messaging, and trust signals from scraped websites.
"""

import re
from typing import List, Dict, Set, Tuple
from collections import Counter

from .models import Competitor, WebsiteData, MarketAnalysis


class ContentExtractor:
    """Extracts structured information from scraped website content."""
    
    # Service-related keywords by industry
    SERVICE_PATTERNS = {
        "plumber": [
            "drain cleaning", "pipe repair", "water heater", "leak detection",
            "sewer line", "garbage disposal", "faucet", "toilet repair",
            "emergency plumbing", "water line", "gas line", "backflow",
            "hydro jetting", "trenchless", "repiping", "sump pump",
            "water softener", "tankless", "bathroom remodel", "kitchen plumbing",
        ],
        "electrician": [
            "electrical repair", "panel upgrade", "rewiring", "outlet",
            "lighting", "ceiling fan", "generator", "ev charger",
            "smoke detector", "surge protection", "electrical inspection",
            "circuit breaker", "emergency electrical", "commercial electrical",
        ],
        "hvac": [
            "ac repair", "heating", "furnace", "air conditioning",
            "duct cleaning", "hvac installation", "thermostat", "heat pump",
            "air quality", "ventilation", "maintenance plan", "emergency hvac",
        ],
        "restaurant": [
            "dine-in", "takeout", "delivery", "catering", "private events",
            "happy hour", "brunch", "lunch special", "dinner",
            "online ordering", "reservations", "group dining",
        ],
        "contractor": [
            "remodeling", "renovation", "addition", "new construction",
            "kitchen remodel", "bathroom remodel", "basement finishing",
            "deck", "roofing", "siding", "windows", "flooring",
            "painting", "drywall", "demolition", "permits",
        ],
        "default": [
            "service", "repair", "installation", "maintenance",
            "consultation", "estimate", "inspection", "emergency",
        ],
    }
    
    # Trust signal patterns
    TRUST_PATTERNS = [
        # Experience
        (r"(\d+)\+?\s*years?\s*(of\s*)?(experience|in business|serving)", "years_experience"),
        (r"since\s*(19|20)\d{2}", "established_since"),
        (r"family[\s-]owned", "family_owned"),
        (r"locally[\s-]owned", "locally_owned"),
        
        # Credentials
        (r"licensed\s*(and|&)?\s*insured", "licensed_insured"),
        (r"fully\s*(licensed|insured)", "licensed_insured"),
        (r"bonded", "bonded"),
        (r"certified", "certified"),
        (r"accredited", "accredited"),
        (r"bbb\s*(a\+?|accredited)", "bbb_rating"),
        
        # Guarantees
        (r"satisfaction\s*guarantee", "satisfaction_guarantee"),
        (r"money[\s-]back\s*guarantee", "money_back"),
        (r"warranty", "warranty"),
        (r"free\s*estimate", "free_estimate"),
        (r"no\s*hidden\s*(fees|charges|costs)", "transparent_pricing"),
        
        # Service quality
        (r"24[\s/]?7", "24_7_service"),
        (r"emergency\s*service", "emergency_service"),
        (r"same[\s-]day\s*service", "same_day"),
        (r"on[\s-]time", "on_time"),
        (r"background\s*check", "background_checked"),
        
        # Social proof
        (r"(\d+)\+?\s*(5[\s-]star)?\s*reviews?", "review_count"),
        (r"(\d+)\+?\s*customers?\s*served", "customers_served"),
        (r"trusted\s*by", "trusted_by"),
    ]
    
    # Pricing patterns
    PRICING_PATTERNS = [
        r"\$\d+",
        r"starting\s*(at|from)\s*\$?\d+",
        r"free\s*estimate",
        r"free\s*quote",
        r"no\s*service\s*call\s*fee",
        r"flat[\s-]rate",
        r"upfront\s*pricing",
        r"financing\s*(available|options)",
        r"payment\s*plans?",
        r"accept\s*(credit\s*cards?|all\s*major)",
    ]
    
    # Tagline/USP patterns
    TAGLINE_PATTERNS = [
        r"your\s+#?\d*\s*(choice|solution|partner)",
        r"the\s+(best|premier|leading|trusted)",
        r"quality\s+you\s+can\s+trust",
        r"we\s+(care|guarantee|promise)",
        r"where\s+quality\s+meets",
        r"experience\s+the\s+difference",
    ]
    
    def __init__(self, business_type: str = "default"):
        self.business_type = business_type.lower()
        self.service_keywords = self._get_service_keywords()
    
    def _get_service_keywords(self) -> List[str]:
        """Get service keywords for the business type."""
        keywords = self.SERVICE_PATTERNS.get(
            self.business_type, 
            self.SERVICE_PATTERNS["default"]
        )
        # Also include default keywords
        if self.business_type != "default":
            keywords = keywords + self.SERVICE_PATTERNS["default"]
        return keywords
    
    def extract_from_website(self, website_data: WebsiteData) -> WebsiteData:
        """
        Extract structured information from website content.
        
        Updates and returns the WebsiteData with extracted info.
        """
        content = website_data.full_text.lower()
        
        # Extract services
        website_data.services = self._extract_services(content)
        
        # Extract trust signals
        website_data.trust_signals = self._extract_trust_signals(content)
        
        # Extract pricing info
        website_data.pricing = self._extract_pricing(content)
        
        # Extract taglines/USPs
        website_data.taglines = self._extract_taglines(website_data.full_text)
        
        # Extract unique points
        website_data.unique_points = self._extract_unique_points(content)
        
        return website_data
    
    def extract_all(self, websites: List[WebsiteData]) -> List[WebsiteData]:
        """Extract information from all websites."""
        return [self.extract_from_website(w) for w in websites]
    
    def _extract_services(self, content: str) -> List[str]:
        """Extract services mentioned in content."""
        found_services = []
        
        for service in self.service_keywords:
            if service.lower() in content:
                # Capitalize properly
                found_services.append(service.title())
        
        return list(set(found_services))
    
    def _extract_trust_signals(self, content: str) -> List[str]:
        """Extract trust signals from content."""
        signals = []
        
        for pattern, signal_type in self.TRUST_PATTERNS:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                # Format the signal nicely
                matched_text = match.group(0)
                signals.append(matched_text.strip().title())
        
        return list(set(signals))
    
    def _extract_pricing(self, content: str) -> List[str]:
        """Extract pricing information from content."""
        pricing_info = []
        
        for pattern in self.PRICING_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, str) and match.strip():
                    pricing_info.append(match.strip())
        
        return list(set(pricing_info))[:10]  # Limit to 10
    
    def _extract_taglines(self, content: str) -> List[str]:
        """Extract taglines and slogans from content."""
        taglines = []
        
        # Look for short, punchy sentences that might be taglines
        sentences = re.split(r'[.!?\n]', content)
        
        for sentence in sentences:
            sentence = sentence.strip()
            words = sentence.split()
            
            # Taglines are usually 3-12 words
            if 3 <= len(words) <= 12:
                # Check for tagline patterns
                sentence_lower = sentence.lower()
                for pattern in self.TAGLINE_PATTERNS:
                    if re.search(pattern, sentence_lower):
                        taglines.append(sentence)
                        break
                
                # Also capture sentences in quotes or that start with capital
                if sentence.startswith('"') or sentence.startswith("'"):
                    taglines.append(sentence.strip('"\''))
        
        return list(set(taglines))[:5]
    
    def _extract_unique_points(self, content: str) -> List[str]:
        """Extract unique selling points."""
        unique_points = []
        
        # Look for "why choose us" type sections
        why_patterns = [
            r"why\s+choose\s+us[:\s]*(.*?)(?=\n\n|\Z)",
            r"what\s+sets\s+us\s+apart[:\s]*(.*?)(?=\n\n|\Z)",
            r"our\s+difference[:\s]*(.*?)(?=\n\n|\Z)",
        ]
        
        for pattern in why_patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                text = match.group(1)
                # Extract bullet points or sentences
                points = re.split(r'[•\-\*\n]', text)
                for point in points:
                    point = point.strip()
                    if 10 < len(point) < 200:
                        unique_points.append(point)
        
        return list(set(unique_points))[:10]


class MarketAnalyzer:
    """Analyzes the competitive market based on extracted data."""
    
    def analyze(
        self,
        business_type: str,
        location: str,
        competitors: List[Competitor],
        websites: List[WebsiteData],
    ) -> MarketAnalysis:
        """
        Analyze the competitive landscape.
        
        Identifies common patterns and opportunities.
        """
        # Aggregate services
        all_services: List[str] = []
        all_trust_signals: List[str] = []
        all_pricing: List[str] = []
        
        for website in websites:
            all_services.extend(website.services)
            all_trust_signals.extend(website.trust_signals)
            all_pricing.extend(website.pricing)
        
        # Count occurrences
        service_counts = Counter(all_services)
        trust_counts = Counter(all_trust_signals)
        
        # Find common (offered by >30% of competitors)
        threshold = max(1, len(websites) * 0.3)
        
        common_services = [
            service for service, count in service_counts.items()
            if count >= threshold
        ]
        
        common_trust = [
            signal for signal, count in trust_counts.items()
            if count >= threshold
        ]
        
        # Find service gaps (mentioned by <20% of competitors)
        gap_threshold = max(1, len(websites) * 0.2)
        service_gaps = [
            service for service, count in service_counts.items()
            if count < gap_threshold and count > 0
        ]
        
        # Determine price range
        price_range = self._analyze_pricing(all_pricing)
        
        # Messaging opportunities
        messaging_opps = self._find_messaging_opportunities(
            common_services, common_trust, websites
        )
        
        return MarketAnalysis(
            business_type=business_type,
            location=location,
            competitors_analyzed=len(websites),
            common_services=common_services[:15],
            common_trust_signals=common_trust[:10],
            price_range=price_range,
            service_gaps=service_gaps[:10],
            messaging_opportunities=messaging_opps,
        )
    
    def _analyze_pricing(self, pricing_info: List[str]) -> str:
        """Analyze pricing patterns."""
        # Extract dollar amounts
        amounts = []
        for info in pricing_info:
            matches = re.findall(r'\$(\d+)', info)
            for match in matches:
                amounts.append(int(match))
        
        if amounts:
            min_price = min(amounts)
            max_price = max(amounts)
            return f"${min_price} - ${max_price}"
        
        return "Pricing not publicly listed"
    
    def _find_messaging_opportunities(
        self,
        common_services: List[str],
        common_trust: List[str],
        websites: List[WebsiteData],
    ) -> List[str]:
        """Find messaging opportunities based on gaps."""
        opportunities = []
        
        # Check for missing trust signals
        potential_trust = [
            "24/7 Service", "Same-Day Service", "Licensed And Insured",
            "Free Estimates", "Satisfaction Guarantee", "Background Checked",
            "Upfront Pricing", "No Hidden Fees",
        ]
        
        common_trust_lower = [t.lower() for t in common_trust]
        
        for trust in potential_trust:
            if trust.lower() not in common_trust_lower:
                opportunities.append(f"Few competitors mention: {trust}")
        
        # Check tagline uniqueness
        all_taglines = []
        for w in websites:
            all_taglines.extend(w.taglines)
        
        if not all_taglines:
            opportunities.append("Most competitors lack clear taglines - opportunity to stand out")
        
        return opportunities[:10]
