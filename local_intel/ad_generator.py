"""
Ad differentiation generator.
Creates advertising angles and copy based on competitive analysis.
"""

from typing import List, Dict, Optional
from .models import (
    Competitor, WebsiteData, MarketAnalysis,
    CompetitiveInsight, InsightType, AdDifferentiator, IntelligenceReport,
    SearchInput,
)


class AdDifferentiationGenerator:
    """Generates advertising differentiation based on competitive intelligence."""
    
    # Templates for different insight types
    INSIGHT_TEMPLATES = {
        InsightType.SERVICE_GAP: {
            "title": "Service Opportunity: {service}",
            "description": "Few competitors in your area prominently offer {service}. This could be a key differentiator.",
            "copy_templates": [
                "Looking for {service}? We specialize in it.",
                "{service} experts - what others can't do, we can.",
            ],
        },
        InsightType.TRUST_DIFFERENTIATOR: {
            "title": "Trust Signal: {signal}",
            "description": "Most competitors don't emphasize {signal}. Highlighting this builds trust.",
            "copy_templates": [
                "{signal} - peace of mind guaranteed.",
                "Unlike others, we're {signal}.",
            ],
        },
        InsightType.PRICING_OPPORTUNITY: {
            "title": "Pricing Angle: {angle}",
            "description": "Competitors lack transparent pricing. This is an opportunity.",
            "copy_templates": [
                "No surprises. Clear pricing upfront.",
                "Know exactly what you'll pay before we start.",
            ],
        },
        InsightType.WEAKNESS_EXPLOIT: {
            "title": "Address Common Complaint: {complaint}",
            "description": "Customers frequently complain about {complaint}. Position against this.",
            "copy_templates": [
                "Tired of {complaint}? We're different.",
                "We actually {solution}.",
            ],
        },
    }
    
    # Industry-specific hooks
    INDUSTRY_HOOKS = {
        "plumber": [
            ("emergency", "Burst pipe at 2 AM? We're there in 60 minutes or less."),
            ("trust", "The plumber your neighbors trust. {review_count}+ 5-star reviews."),
            ("pricing", "No hidden fees. The price we quote is the price you pay."),
            ("quality", "Fixed right the first time, guaranteed."),
            ("speed", "Same-day service. Because leaks don't wait."),
        ],
        "electrician": [
            ("safety", "Licensed electricians who put your family's safety first."),
            ("emergency", "Electrical emergency? We respond 24/7."),
            ("trust", "Background-checked electricians you can trust in your home."),
            ("modern", "Smart home ready. We install the future."),
        ],
        "restaurant": [
            ("quality", "Fresh ingredients. Made from scratch. Taste the difference."),
            ("local", "Family recipes. Local ingredients. Community love."),
            ("experience", "More than a meal. An experience."),
            ("convenience", "Order online. Ready when you are."),
        ],
        "contractor": [
            ("trust", "Licensed, bonded, and insured. Your project protected."),
            ("quality", "Craftsmanship that lasts. Guaranteed."),
            ("communication", "Weekly updates. No surprises. Your project, your way."),
            ("local", "{years} years transforming {location} homes."),
        ],
        "default": [
            ("trust", "Trusted by your neighbors. Loved by our customers."),
            ("quality", "Quality service. Fair prices. Guaranteed."),
            ("local", "Locally owned. Community focused."),
            ("response", "Fast response. Professional service."),
        ],
    }
    
    def __init__(self, business_type: str = "default"):
        self.business_type = business_type.lower()
    
    def generate_insights(
        self,
        market_analysis: MarketAnalysis,
        websites: List[WebsiteData],
    ) -> List[CompetitiveInsight]:
        """Generate competitive insights from market analysis."""
        insights = []
        
        # Service gap insights
        for gap in market_analysis.service_gaps[:5]:
            insight = CompetitiveInsight(
                insight_type=InsightType.SERVICE_GAP,
                title=f"Service Opportunity: {gap}",
                description=f"Only {self._count_offering(gap, websites)} of {len(websites)} competitors prominently offer {gap}.",
                evidence=[f"{gap} mentioned by few competitors"],
                suggested_copy=[
                    f"Need {gap.lower()}? We're the experts.",
                    f"Specialized {gap.lower()} services others can't match.",
                ],
                priority=1,
            )
            insights.append(insight)
        
        # Trust signal opportunities
        missing_trust = self._find_missing_trust_signals(websites)
        for signal in missing_trust[:3]:
            insight = CompetitiveInsight(
                insight_type=InsightType.TRUST_DIFFERENTIATOR,
                title=f"Trust Opportunity: {signal}",
                description=f"Most competitors don't emphasize '{signal}' - this builds customer confidence.",
                evidence=[f"Signal '{signal}' rarely mentioned by competitors"],
                suggested_copy=[
                    f"{signal} - peace of mind included.",
                    f"We're proud to be {signal.lower()}.",
                ],
                priority=2,
            )
            insights.append(insight)
        
        # Pricing transparency opportunity
        if self._check_pricing_opacity(websites):
            insight = CompetitiveInsight(
                insight_type=InsightType.PRICING_OPPORTUNITY,
                title="Pricing Transparency Gap",
                description="Most competitors hide their pricing. Transparent pricing builds trust.",
                evidence=["Majority of competitor sites don't show prices"],
                suggested_copy=[
                    "Upfront pricing. No surprises.",
                    "Know your cost before we start.",
                    "Free estimates. Honest pricing.",
                ],
                priority=1,
            )
            insights.append(insight)
        
        # Messaging opportunities from analysis
        for opp in market_analysis.messaging_opportunities[:3]:
            insight = CompetitiveInsight(
                insight_type=InsightType.MESSAGING_ANGLE,
                title=opp,
                description="Messaging gap identified in competitor analysis.",
                evidence=[],
                suggested_copy=[],
                priority=3,
            )
            insights.append(insight)
        
        return insights
    
    def generate_differentiators(
        self,
        insights: List[CompetitiveInsight],
        market_analysis: MarketAnalysis,
    ) -> List[AdDifferentiator]:
        """Generate advertising differentiators from insights."""
        differentiators = []
        
        # Get industry-specific hooks
        hooks = self.INDUSTRY_HOOKS.get(
            self.business_type,
            self.INDUSTRY_HOOKS["default"]
        )
        
        # Create differentiators from hooks
        for hook_type, hook_text in hooks:
            # Customize hook with data if available
            customized = hook_text.format(
                review_count="100",  # Placeholder
                years="10",  # Placeholder
                location=market_analysis.location,
            )
            
            differentiator = AdDifferentiator(
                angle_name=hook_type.title() + " Angle",
                hook=customized,
                supporting_points=self._get_supporting_points(hook_type, insights),
                proof_needed=self._get_proof_needed(hook_type),
                best_for=self._get_best_platform(hook_type),
            )
            differentiators.append(differentiator)
        
        # Create differentiators from high-priority insights
        for insight in insights[:3]:
            if insight.suggested_copy:
                differentiator = AdDifferentiator(
                    angle_name=insight.title,
                    hook=insight.suggested_copy[0],
                    supporting_points=insight.evidence,
                    proof_needed="Customer testimonial or demonstration",
                    best_for="Facebook/Instagram Ads",
                )
                differentiators.append(differentiator)
        
        return differentiators
    
    def generate_headlines(
        self,
        market_analysis: MarketAnalysis,
        differentiators: List[AdDifferentiator],
    ) -> List[str]:
        """Generate headline suggestions."""
        headlines = []
        
        # From differentiators
        for diff in differentiators[:5]:
            headlines.append(diff.hook)
        
        # Generic industry headlines
        industry_headlines = {
            "plumber": [
                "Your Local Plumbing Experts",
                "Fast. Reliable. Affordable.",
                "Plumbing Problems? Solved.",
            ],
            "electrician": [
                "Power You Can Trust",
                "Safe. Reliable. Professional.",
                "Electrical Done Right",
            ],
            "restaurant": [
                "Taste the Difference",
                "Where Flavor Meets Freshness",
                "Your New Favorite Spot",
            ],
            "contractor": [
                "Building Your Vision",
                "Quality Craftsmanship. Fair Prices.",
                "Your Home, Transformed",
            ],
            "default": [
                "Service You Can Trust",
                "Quality. Value. Results.",
                "The Local Choice",
            ],
        }
        
        industry_specific = industry_headlines.get(
            self.business_type,
            industry_headlines["default"]
        )
        headlines.extend(industry_specific)
        
        return list(set(headlines))[:10]
    
    def generate_taglines(self, market_analysis: MarketAnalysis) -> List[str]:
        """Generate tagline suggestions."""
        taglines = [
            f"Serving {market_analysis.location} with pride",
            "Quality you can trust, service you deserve",
            "Your satisfaction, guaranteed",
            "Locally owned, community trusted",
            "Excellence in every job",
            "Where quality meets reliability",
            "Professional service, personal touch",
            "Done right. Done on time.",
        ]
        
        return taglines[:8]
    
    def generate_trust_signals_to_use(
        self,
        market_analysis: MarketAnalysis,
    ) -> List[str]:
        """Suggest trust signals to emphasize based on competitor gaps."""
        # Standard trust signals
        all_signals = [
            "Licensed & Insured",
            "Free Estimates",
            "Satisfaction Guaranteed",
            "24/7 Emergency Service",
            "Same-Day Service Available",
            "Background-Checked Technicians",
            "Upfront Pricing",
            "Locally Owned & Operated",
            "Family-Owned Since [Year]",
            "[X]+ Years Experience",
            "[X]+ 5-Star Reviews",
            "BBB Accredited",
        ]
        
        # Prioritize signals NOT commonly used by competitors
        uncommon = []
        common_lower = [s.lower() for s in market_analysis.common_trust_signals]
        
        for signal in all_signals:
            signal_lower = signal.lower()
            is_common = any(c in signal_lower or signal_lower in c for c in common_lower)
            if not is_common:
                uncommon.append(signal)
        
        # Return uncommon first, then common
        return uncommon[:6] + market_analysis.common_trust_signals[:4]
    
    def _count_offering(self, service: str, websites: List[WebsiteData]) -> int:
        """Count how many competitors offer a service."""
        count = 0
        for website in websites:
            if any(service.lower() in s.lower() for s in website.services):
                count += 1
        return count
    
    def _find_missing_trust_signals(self, websites: List[WebsiteData]) -> List[str]:
        """Find trust signals that are rarely used."""
        desired_signals = [
            "Background Checked",
            "Same Day Service",
            "Upfront Pricing",
            "Satisfaction Guarantee",
            "On Time Guarantee",
        ]
        
        all_signals = []
        for w in websites:
            all_signals.extend([s.lower() for s in w.trust_signals])
        
        missing = []
        for signal in desired_signals:
            if not any(signal.lower() in s for s in all_signals):
                missing.append(signal)
        
        return missing
    
    def _check_pricing_opacity(self, websites: List[WebsiteData]) -> bool:
        """Check if most competitors hide pricing."""
        with_pricing = sum(1 for w in websites if w.pricing)
        return with_pricing < len(websites) * 0.3
    
    def _get_supporting_points(
        self,
        hook_type: str,
        insights: List[CompetitiveInsight],
    ) -> List[str]:
        """Get supporting points for a hook type."""
        points_map = {
            "emergency": ["Fast response time", "Available 24/7", "No extra fees for emergencies"],
            "trust": ["Licensed and insured", "Background-checked", "Thousands of happy customers"],
            "pricing": ["Free estimates", "No hidden fees", "Price match guarantee"],
            "quality": ["Trained professionals", "Premium materials", "Satisfaction guaranteed"],
            "speed": ["Same-day availability", "On-time guarantee", "Efficient service"],
            "local": ["Community involvement", "Local knowledge", "Supporting local economy"],
        }
        return points_map.get(hook_type, ["Quality service", "Professional team"])
    
    def _get_proof_needed(self, hook_type: str) -> str:
        """Get proof suggestions for a hook type."""
        proof_map = {
            "emergency": "Show response time statistics or customer testimonial about emergency service",
            "trust": "Display review count, ratings, certifications prominently",
            "pricing": "Show sample pricing or comparison with competitors",
            "quality": "Before/after photos, warranty information",
            "speed": "Same-day booking calendar, response time data",
            "local": "Team photos, community involvement images",
        }
        return proof_map.get(hook_type, "Customer testimonials and reviews")
    
    def _get_best_platform(self, hook_type: str) -> str:
        """Get best platform for a hook type."""
        platform_map = {
            "emergency": "Google Ads (search intent)",
            "trust": "Facebook/Instagram (social proof)",
            "pricing": "Google Ads, Website",
            "quality": "Instagram, Website portfolio",
            "speed": "Google Ads, Google Business Profile",
            "local": "Facebook, Nextdoor, Local print",
        }
        return platform_map.get(hook_type, "All platforms")
