"""
Output generators for ad research artifacts.
Produces HookBank, AnglePlaybook, ObjectionHandling, etc.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from .models import (
    Theme, VoCSignal, SignalType, ResearchInput,
    VoiceOfCustomerBrief, AnglePlaybook, Angle,
    HookBank, Hook, ObjectionHandling, Objection,
    SourceMap, Source, ResearchOutput, Post,
)


class HookGenerator:
    """Generates ad hooks from themes and signals."""
    
    # Hook templates by tone
    HOOK_TEMPLATES = {
        "curious": [
            "What if {topic} was actually {benefit}?",
            "The truth about {topic} nobody tells you",
            "Why {audience} are switching to {solution}",
            "I tried {topic} for 30 days. Here's what happened.",
        ],
        "urgent": [
            "Stop {pain_point} right now",
            "You're probably making this {topic} mistake",
            "Before you {action}, watch this",
            "{pain_point}? There's a better way.",
        ],
        "empathetic": [
            "Tired of {pain_point}? You're not alone.",
            "I get it. {pain_point} is frustrating.",
            "We've all been there with {topic}",
            "Finally, a {solution} that actually works",
        ],
        "social_proof": [
            "Why thousands are choosing {solution}",
            "The {topic} secret {audience} swear by",
            "What {audience} wish they knew about {topic}",
            "Join the {audience} who discovered {benefit}",
        ],
        "contrarian": [
            "Everything you know about {topic} is wrong",
            "Why I stopped {common_action} (and you should too)",
            "The {topic} industry doesn't want you to know this",
            "Unpopular opinion: {contrarian_take}",
        ],
    }
    
    def generate_hooks(
        self,
        themes: List[Theme],
        research_input: ResearchInput,
        hooks_per_theme: int = 3,
    ) -> HookBank:
        """Generate hooks from themes."""
        hooks: List[Hook] = []
        
        for theme in themes[:8]:  # Top 8 themes
            theme_hooks = self._generate_theme_hooks(
                theme, research_input, hooks_per_theme
            )
            hooks.extend(theme_hooks)
        
        return HookBank(hooks=hooks)
    
    def _generate_theme_hooks(
        self,
        theme: Theme,
        research_input: ResearchInput,
        count: int,
    ) -> List[Hook]:
        """Generate hooks for a single theme."""
        hooks: List[Hook] = []
        
        # Determine best tones for this theme
        tones = self._select_tones_for_theme(theme)
        
        for i, tone in enumerate(tones[:count]):
            templates = self.HOOK_TEMPLATES.get(tone, self.HOOK_TEMPLATES["curious"])
            template = templates[i % len(templates)]
            
            # Fill in template
            hook_text = self._fill_template(template, theme, research_input)
            
            # Generate visual suggestion
            visual = self._suggest_visual(theme, tone)
            
            hook = Hook(
                text=hook_text,
                mapped_theme=theme.name,
                tone=tone,
                recommended_opening_visual=visual,
            )
            hooks.append(hook)
        
        # Also add hooks from actual quotes
        for quote in theme.example_quotes[:2]:
            if len(quote) < 100:  # Short quotes work as hooks
                hook = Hook(
                    text=f'"{quote}"',
                    mapped_theme=theme.name,
                    tone="authentic",
                    recommended_opening_visual="Text overlay on relatable background",
                )
                hooks.append(hook)
        
        return hooks
    
    def _select_tones_for_theme(self, theme: Theme) -> List[str]:
        """Select appropriate tones based on theme content."""
        tones = []
        
        theme_lower = theme.name.lower()
        
        # Map themes to tones
        if any(kw in theme_lower for kw in ["price", "cost", "value"]):
            tones = ["urgent", "contrarian", "social_proof"]
        elif any(kw in theme_lower for kw in ["quality", "reliability"]):
            tones = ["empathetic", "social_proof", "curious"]
        elif any(kw in theme_lower for kw in ["convenience", "easy"]):
            tones = ["curious", "empathetic", "urgent"]
        elif any(kw in theme_lower for kw in ["trust", "scam"]):
            tones = ["empathetic", "social_proof", "contrarian"]
        else:
            tones = ["curious", "empathetic", "social_proof"]
        
        return tones
    
    def _fill_template(
        self,
        template: str,
        theme: Theme,
        research_input: ResearchInput,
    ) -> str:
        """Fill in a hook template with actual content."""
        # Build replacement dict
        replacements = {
            "{topic}": research_input.product,
            "{audience}": research_input.audience,
            "{solution}": research_input.product,
            "{benefit}": theme.desired_outcomes[0] if theme.desired_outcomes else "easier",
            "{pain_point}": theme.common_objections[0] if theme.common_objections else f"{theme.name} problems",
            "{action}": f"buying {research_input.product}",
            "{common_action}": f"using traditional {research_input.market} solutions",
            "{contrarian_take}": f"{research_input.product} isn't what you think",
        }
        
        result = template
        for key, value in replacements.items():
            result = result.replace(key, value)
        
        return result
    
    def _suggest_visual(self, theme: Theme, tone: str) -> str:
        """Suggest an opening visual for the hook."""
        visuals = {
            "curious": "Close-up of product with mysterious lighting",
            "urgent": "Person frustrated, then discovering solution",
            "empathetic": "Relatable everyday situation",
            "social_proof": "Montage of happy customers or testimonials",
            "contrarian": "Dramatic reveal or unexpected comparison",
            "authentic": "UGC-style testimonial clip",
        }
        return visuals.get(tone, "Product demonstration")


class AngleGenerator:
    """Generates advertising angles from themes."""
    
    def generate_angles(
        self,
        themes: List[Theme],
        research_input: ResearchInput,
    ) -> AnglePlaybook:
        """Generate advertising angles from themes."""
        angles: List[Angle] = []
        
        for theme in themes[:6]:  # Top 6 themes become angles
            angle = self._theme_to_angle(theme, research_input)
            angles.append(angle)
        
        return AnglePlaybook(angles=angles)
    
    def _theme_to_angle(
        self,
        theme: Theme,
        research_input: ResearchInput,
    ) -> Angle:
        """Convert a theme into an advertising angle."""
        # Determine target emotion
        emotion = self._determine_emotion(theme)
        
        # Create promise based on theme
        promise = self._create_promise(theme, research_input)
        
        # Supporting points from quotes and keywords
        supporting_points = []
        
        for quote in theme.example_quotes[:3]:
            # Summarize quote into point
            if len(quote) < 80:
                supporting_points.append(f'Customers say: "{quote}"')
        
        for outcome in theme.desired_outcomes[:2]:
            supporting_points.append(f"Delivers: {outcome}")
        
        # Add keyword-based points
        if theme.keywords:
            supporting_points.append(
                f"Key concerns addressed: {', '.join(theme.keywords[:5])}"
            )
        
        return Angle(
            name=f"{theme.name} Angle",
            promise=promise,
            target_emotion=emotion,
            best_for_audience=research_input.audience,
            supporting_points=supporting_points,
        )
    
    def _determine_emotion(self, theme: Theme) -> str:
        """Determine the target emotion for an angle."""
        theme_lower = theme.name.lower()
        
        emotion_map = {
            "price": "relief",
            "quality": "confidence",
            "convenience": "ease",
            "reliability": "trust",
            "customer service": "security",
            "shipping": "anticipation",
            "taste": "pleasure",
            "health": "empowerment",
            "subscription": "freedom",
            "comparison": "certainty",
            "trust": "security",
            "experience": "excitement",
        }
        
        for key, emotion in emotion_map.items():
            if key in theme_lower:
                return emotion
        
        return "curiosity"
    
    def _create_promise(
        self,
        theme: Theme,
        research_input: ResearchInput,
    ) -> str:
        """Create an ad promise for the angle."""
        if theme.desired_outcomes:
            outcome = theme.desired_outcomes[0]
            return f"{research_input.product} delivers {outcome}"
        
        if theme.common_objections:
            objection = theme.common_objections[0]
            return f"Say goodbye to {objection} with {research_input.product}"
        
        return f"Discover why {research_input.audience} love {research_input.product}"


class ObjectionHandler:
    """Generates objection handling content."""
    
    def generate_objection_handling(
        self,
        themes: List[Theme],
        signals: List[VoCSignal],
        research_input: ResearchInput,
    ) -> ObjectionHandling:
        """Generate objection handling from themes and signals."""
        objections: List[Objection] = []
        
        # Get objection signals
        objection_signals = [
            s for s in signals 
            if s.signal_type == SignalType.OBJECTION
        ]
        
        # Group objections by theme
        theme_objections: Dict[str, List[str]] = {}
        for theme in themes:
            theme_objections[theme.name] = theme.common_objections
        
        # Create objection handlers
        for theme in themes:
            for obj_text in theme.common_objections[:2]:
                objection = self._create_objection_handler(
                    obj_text, theme, research_input
                )
                objections.append(objection)
        
        # Also handle generic objections from signals
        seen_objections = set()
        for signal in objection_signals[:10]:
            obj_summary = self._summarize_objection(signal.text)
            if obj_summary and obj_summary not in seen_objections:
                seen_objections.add(obj_summary)
                objection = Objection(
                    objection=obj_summary,
                    rebuttal_lines=self._generate_generic_rebuttals(obj_summary, research_input),
                    proof_visuals=["Customer testimonial", "Product demonstration"],
                )
                objections.append(objection)
        
        return ObjectionHandling(objections=objections[:15])
    
    def _create_objection_handler(
        self,
        objection_text: str,
        theme: Theme,
        research_input: ResearchInput,
    ) -> Objection:
        """Create an objection handler with rebuttals."""
        rebuttals = []
        proof_visuals = []
        
        objection_lower = objection_text.lower()
        
        # Generate rebuttals based on objection type
        if any(kw in objection_lower for kw in ["expensive", "price", "cost", "afford"]):
            rebuttals = [
                f"Consider the cost of NOT having {research_input.product}",
                "Our customers save money in the long run because...",
                "We offer flexible options to fit any budget",
            ]
            proof_visuals = ["ROI calculator", "Price comparison chart", "Value breakdown"]
        
        elif any(kw in objection_lower for kw in ["trust", "scam", "legit", "real"]):
            rebuttals = [
                "We're backed by thousands of verified reviews",
                "Here's our story and why we started this...",
                "Try risk-free with our guarantee",
            ]
            proof_visuals = ["Trust badges", "Review compilation", "Behind-the-scenes"]
        
        elif any(kw in objection_lower for kw in ["work", "effective", "actually"]):
            rebuttals = [
                "Here's exactly how it works...",
                "See these real results from customers like you",
                "We guarantee results or your money back",
            ]
            proof_visuals = ["Demo video", "Before/after", "Customer results montage"]
        
        else:
            rebuttals = [
                f"Great question! Here's what you should know...",
                f"We designed {research_input.product} specifically for this",
                "Our customers had the same concern, and here's what they found",
            ]
            proof_visuals = ["FAQ video", "Customer testimonial"]
        
        return Objection(
            objection=objection_text,
            rebuttal_lines=rebuttals,
            proof_visuals=proof_visuals,
        )
    
    def _summarize_objection(self, text: str, max_length: int = 100) -> str:
        """Summarize an objection to a short statement."""
        # Take first sentence or truncate
        sentences = text.split('.')
        if sentences:
            summary = sentences[0].strip()
            if len(summary) > max_length:
                summary = summary[:max_length] + "..."
            return summary
        return ""
    
    def _generate_generic_rebuttals(
        self,
        objection: str,
        research_input: ResearchInput,
    ) -> List[str]:
        """Generate generic rebuttals for an objection."""
        return [
            f"We understand this concern about {research_input.product}",
            "Here's what our customers say after trying it...",
            f"Let us show you why {research_input.product} is different",
        ]


class SourceMapper:
    """Tracks and maps sources used in research."""
    
    def generate_source_map(
        self,
        posts: List[Post],
        subreddit_stats: Dict[str, int],
    ) -> SourceMap:
        """Generate a source map from collected posts."""
        sources: List[Source] = []
        
        # Group posts by subreddit
        subreddit_posts: Dict[str, List[Post]] = {}
        for post in posts:
            if post.subreddit not in subreddit_posts:
                subreddit_posts[post.subreddit] = []
            subreddit_posts[post.subreddit].append(post)
        
        for subreddit, sub_posts in subreddit_posts.items():
            # Get date range
            if sub_posts:
                dates = [p.created_datetime for p in sub_posts]
                min_date = min(dates).strftime("%Y-%m-%d")
                max_date = max(dates).strftime("%Y-%m-%d")
                date_range = f"{min_date} to {max_date}"
            else:
                date_range = "N/A"
            
            # Get comment count
            comment_count = subreddit_stats.get(subreddit, 0)
            
            # Use first post URL as example
            post_url = sub_posts[0].full_url if sub_posts else ""
            
            source = Source(
                subreddit=f"r/{subreddit}",
                post_url=post_url,
                comment_count_used=comment_count,
                date_range=date_range,
            )
            sources.append(source)
        
        return SourceMap(sources=sources)


class OutputGenerator:
    """Main output generator combining all components."""
    
    def __init__(self):
        self.hook_generator = HookGenerator()
        self.angle_generator = AngleGenerator()
        self.objection_handler = ObjectionHandler()
        self.source_mapper = SourceMapper()
    
    def generate_all(
        self,
        themes: List[Theme],
        signals: List[VoCSignal],
        posts: List[Post],
        research_input: ResearchInput,
        language_bank: List[str],
    ) -> ResearchOutput:
        """Generate all output artifacts."""
        # Build subreddit stats
        subreddit_stats: Dict[str, int] = {}
        for signal in signals:
            sub = signal.source_subreddit
            subreddit_stats[sub] = subreddit_stats.get(sub, 0) + 1
        
        # Generate VoC Brief
        voc_brief = VoiceOfCustomerBrief(
            product=research_input.product,
            audience=research_input.audience,
            market=research_input.market,
            top_themes=themes,
            language_bank=language_bank,
        )
        
        # Generate Angle Playbook
        angle_playbook = self.angle_generator.generate_angles(themes, research_input)
        
        # Generate Hook Bank
        hook_bank = self.hook_generator.generate_hooks(themes, research_input)
        
        # Generate Objection Handling
        objection_handling = self.objection_handler.generate_objection_handling(
            themes, signals, research_input
        )
        
        # Generate Source Map
        source_map = self.source_mapper.generate_source_map(posts, subreddit_stats)
        
        return ResearchOutput(
            voc_brief=voc_brief,
            angle_playbook=angle_playbook,
            hook_bank=hook_bank,
            objection_handling=objection_handling,
            source_map=source_map,
        )
