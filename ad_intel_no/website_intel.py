"""
Website Intelligence Agent
Scrapes competitor websites for messaging, offers, and positioning.
Uses Firecrawl or Jina for web scraping.
"""

import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import requests


@dataclass
class WebsiteData:
    """Data extracted from a competitor website."""

    url: str
    business_name: str = ""

    # Extracted content
    headline: str = ""
    tagline: str = ""
    value_propositions: List[str] = field(default_factory=list)
    services: List[str] = field(default_factory=list)
    offers: List[str] = field(default_factory=list)
    trust_signals: List[str] = field(default_factory=list)
    ctas: List[str] = field(default_factory=list)
    phone: str = ""

    # Raw content for analysis
    raw_text: str = ""


@dataclass
class WebsiteAnalysis:
    """Analysis of competitor websites."""

    business_type: str
    location: str
    websites_analyzed: int

    websites: List[WebsiteData] = field(default_factory=list)

    # Aggregated insights
    common_headlines: List[str] = field(default_factory=list)
    common_offers: List[str] = field(default_factory=list)
    common_trust_signals: List[str] = field(default_factory=list)
    common_ctas: List[str] = field(default_factory=list)
    messaging_patterns: List[str] = field(default_factory=list)
    differentiation_opportunities: List[str] = field(default_factory=list)


class WebsiteIntelAgent:
    """
    Scrapes competitor websites for messaging analysis.

    Uses Firecrawl (preferred) or Jina Reader for scraping.
    Falls back to basic requests if neither available.
    """

    def __init__(
        self,
        firecrawl_key: Optional[str] = None,
        jina_key: Optional[str] = None,
    ):
        self.firecrawl_key = firecrawl_key or os.getenv("FIRECRAWL_API_KEY")
        self.jina_key = jina_key or os.getenv("JINA_API_KEY")

        # Determine which scraper to use
        if self.firecrawl_key and self.firecrawl_key != "your_firecrawl_key_here":
            self.scraper = "firecrawl"
        elif self.jina_key:
            self.scraper = "jina"
        else:
            self.scraper = "basic"
            print("    ⚠️ No Firecrawl/Jina key - using basic scraper (limited)")

    def analyze_competitor_websites(
        self,
        urls: List[str],
        business_type: str,
        location: str,
    ) -> WebsiteAnalysis:
        """
        Analyze competitor websites.

        Args:
            urls: List of competitor website URLs
            business_type: Type of business
            location: Location context

        Returns:
            WebsiteAnalysis with messaging insights
        """
        print(f"\n  🌐 Website Intelligence: Analyzing {len(urls)} sites")

        websites = []
        for url in urls[:5]:  # Limit to 5 sites
            print(f"    Scraping: {url}")
            data = self._scrape_website(url)
            if data:
                websites.append(data)

        print(f"    Successfully scraped {len(websites)} websites")

        # Analyze patterns
        analysis = self._analyze_patterns(websites, business_type, location)

        return analysis

    def _scrape_website(self, url: str) -> Optional[WebsiteData]:
        """Scrape a website using available method."""
        try:
            if self.scraper == "firecrawl":
                return self._scrape_firecrawl(url)
            elif self.scraper == "jina":
                return self._scrape_jina(url)
            else:
                return self._scrape_basic(url)
        except Exception as e:
            print(f"      ⚠️ Error scraping {url}: {e}")
            return None

    def _scrape_firecrawl(self, url: str) -> Optional[WebsiteData]:
        """Scrape using Firecrawl API."""
        try:
            headers = {
                "Authorization": f"Bearer {self.firecrawl_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "url": url,
                "formats": ["markdown"],
            }

            response = requests.post(
                "https://api.firecrawl.dev/v1/scrape",
                headers=headers,
                json=payload,
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                markdown = data.get("data", {}).get("markdown", "")

                return self._parse_content(url, markdown)
            else:
                print(f"      Firecrawl error: {response.status_code}")
                return None

        except Exception as e:
            print(f"      Firecrawl error: {e}")
            return None

    def _scrape_jina(self, url: str) -> Optional[WebsiteData]:
        """Scrape using Jina Reader."""
        try:
            # Jina Reader: just prepend r.jina.ai to any URL
            jina_url = f"https://r.jina.ai/{url}"

            headers = {}
            if self.jina_key:
                headers["Authorization"] = f"Bearer {self.jina_key}"

            response = requests.get(jina_url, headers=headers, timeout=30)

            if response.status_code == 200:
                return self._parse_content(url, response.text)
            else:
                print(f"      Jina error: {response.status_code}")
                return None

        except Exception as e:
            print(f"      Jina error: {e}")
            return None

    def _scrape_basic(self, url: str) -> Optional[WebsiteData]:
        """Basic scraping with requests + simple parsing."""
        try:
            headers = {"User-Agent": "Mozilla/5.0 (compatible; AdResearchBot/1.0)"}

            response = requests.get(url, headers=headers, timeout=15)

            if response.status_code == 200:
                # Basic HTML to text conversion
                html = response.text

                # Remove script/style tags
                html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
                html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL)

                # Extract text
                text = re.sub(r"<[^>]+>", " ", html)
                text = re.sub(r"\s+", " ", text).strip()

                return self._parse_content(url, text[:5000])

            return None

        except Exception as e:
            print(f"      Basic scrape error: {e}")
            return None

    def _parse_content(self, url: str, content: str) -> WebsiteData:
        """Parse website content to extract key elements."""
        data = WebsiteData(url=url, raw_text=content[:3000])

        content_lower = content.lower()

        # Extract business name from URL
        domain = url.split("//")[-1].split("/")[0]
        data.business_name = domain.replace("www.", "").split(".")[0].title()

        # Find headline (usually first major text)
        lines = [
            l.strip() for l in content.split("\n") if l.strip() and len(l.strip()) > 10
        ]
        if lines:
            data.headline = lines[0][:100]

        # Extract value propositions
        value_prop_patterns = [
            r"we (?:offer|provide|specialize|deliver)",
            r"our (?:team|experts|professionals)",
            r"(?:years|decades) of experience",
            r"satisfaction guaranteed",
            r"free (?:estimate|quote|consultation)",
        ]

        for pattern in value_prop_patterns:
            matches = re.findall(f".{{0,50}}{pattern}.{{0,50}}", content_lower)
            for match in matches[:2]:
                data.value_propositions.append(match.strip())

        # Extract offers
        offer_patterns = [
            r"\d+%\s*off",
            r"\$\d+\s*off",
            r"free\s+\w+",
            r"special\s+offer",
            r"limited\s+time",
            r"discount",
            r"save\s+\$?\d+",
        ]

        for pattern in offer_patterns:
            matches = re.findall(f".{{0,30}}{pattern}.{{0,30}}", content_lower)
            for match in matches[:2]:
                data.offers.append(match.strip())

        # Extract trust signals
        trust_patterns = [
            (r"licensed", "licensed"),
            (r"insured", "insured"),
            (r"certified", "certified"),
            (r"\d+\s*years", "years experience"),
            (r"family[\s-]owned", "family owned"),
            (r"locally[\s-]owned", "locally owned"),
            (r"bbb", "BBB accredited"),
            (r"satisfaction\s*guarantee", "satisfaction guaranteed"),
            (r"warranty", "warranty offered"),
            (r"\d+\s*reviews", "customer reviews"),
        ]

        for pattern, label in trust_patterns:
            if re.search(pattern, content_lower):
                data.trust_signals.append(label)

        # Extract CTAs
        cta_patterns = [
            r"call\s+(?:us\s+)?(?:now|today)",
            r"get\s+(?:a\s+)?(?:free\s+)?(?:quote|estimate)",
            r"schedule\s+(?:now|today|online)",
            r"book\s+(?:now|online|today)",
            r"contact\s+us",
            r"request\s+(?:a\s+)?(?:quote|service)",
        ]

        for pattern in cta_patterns:
            if re.search(pattern, content_lower):
                match = re.search(pattern, content_lower)
                if match:
                    data.ctas.append(match.group().title())

        # Extract phone number
        phone_match = re.search(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", content)
        if phone_match:
            data.phone = phone_match.group()

        return data

    def _analyze_patterns(
        self,
        websites: List[WebsiteData],
        business_type: str,
        location: str,
    ) -> WebsiteAnalysis:
        """Analyze patterns across websites."""
        from collections import Counter

        all_trust_signals = []
        all_ctas = []
        all_offers = []
        all_value_props = []

        for site in websites:
            all_trust_signals.extend(site.trust_signals)
            all_ctas.extend(site.ctas)
            all_offers.extend(site.offers)
            all_value_props.extend(site.value_propositions)

        # Count frequencies
        trust_counter = Counter(all_trust_signals)
        cta_counter = Counter(all_ctas)

        # Find differentiation opportunities
        opportunities = []
        common_signals = {s for s, _ in trust_counter.most_common(5)}

        potential_differentiators = [
            "eco-friendly",
            "same-day service",
            "24/7 availability",
            "senior discount",
            "military discount",
            "financing available",
            "women-owned",
            "veteran-owned",
            "bilingual staff",
        ]

        for diff in potential_differentiators:
            if diff not in common_signals:
                opportunities.append(f"Differentiate with: {diff}")

        # Messaging patterns
        patterns = []
        if trust_counter.most_common(1):
            top_signal = trust_counter.most_common(1)[0][0]
            patterns.append(f"Most emphasize: {top_signal}")

        if cta_counter.most_common(1):
            top_cta = cta_counter.most_common(1)[0][0]
            patterns.append(f"Common CTA: {top_cta}")

        return WebsiteAnalysis(
            business_type=business_type,
            location=location,
            websites_analyzed=len(websites),
            websites=websites,
            common_headlines=[w.headline for w in websites if w.headline][:5],
            common_offers=list(set(all_offers))[:5],
            common_trust_signals=[s for s, _ in trust_counter.most_common(5)],
            common_ctas=[c for c, _ in cta_counter.most_common(5)],
            messaging_patterns=patterns,
            differentiation_opportunities=opportunities[:5],
        )
