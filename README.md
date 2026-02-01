# AdBoard AI - Multi-Agent Storyboard Generator

![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)

> A multi-agent system that helps small businesses create professional ad storyboards without expensive agency fees.

## Problem

Small businesses typically spend $5,000-$50,000 on ad agencies just for storyboarding and pre-production. They lack the resources for:
- Market research on what ads work in their industry
- Professional scriptwriting
- Visual storyboarding
- Cost estimation for production

## Solution

AdBoard AI is a swarm of specialized AI agents that:
1. **Research** viral ads in your industry
2. **Write** a compelling 30-60 second script
3. **Generate** a visual storyboard (6-12 keyframes)
4. **Create** a professional voiceover
5. **Estimate** production costs and find filming locations
6. **Deliver** a PDF screenplay package

## Agent Architecture

```
User Query (via ASI:One)
         │
         ▼
┌─────────────────────────────────────┐
│      ORCHESTRATOR AGENT             │
│   (Chat Protocol / Agentverse)      │
└─────────────────┬───────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
    ▼             ▼             ▼
┌────────┐  ┌──────────┐  ┌────────────┐
│RESEARCH│  │ CREATIVE │  │ PRODUCTION │
│ AGENT  │  │ DIRECTOR │  │   AGENT    │
└────────┘  └──────────┘  └────────────┘
                │
      ┌─────────┼─────────┐
      │         │         │
      ▼         ▼         ▼
  Script   Storyboard  Voiceover
  Writer   Generator    Agent
```

## Agents Deployed on Agentverse

| Agent Name | Address | Description |
|------------|---------|-------------|
| AdBoard Orchestrator | `agent1q...` | Main user-facing agent with Chat Protocol |
| Research Agent | `agent1q...` | Analyzes viral ads in target industry |
| Creative Director | `agent1q...` | Coordinates script, storyboard, voiceover |
| Production Agent | `agent1q...` | Cost estimation and location scouting |

## Tech Stack

- **Framework**: uAgents (Fetch.AI)
- **Deployment**: Agentverse
- **LLM**: Groq (Llama 3.3 70B)
- **Image Generation**: Google Vertex AI (Imagen) / Pollinations.ai (FLUX)
- **Voice**: ElevenLabs
- **Research**: YouTube Data API v3
- **Locations**: Google Places API
- **PDF Generation**: ReportLab

## Quick Start

```bash
# Install dependencies
pip install uagents groq elevenlabs reportlab requests

# Set environment variables
export GROQ_API_KEY="your-key"
export ELEVENLABS_API_KEY="your-key"
export YOUTUBE_API_KEY="your-key"
export REPLICATE_API_TOKEN="your-key"

# Run the orchestrator
python agents/orchestrator.py
```

## Demo

[Link to 3-5 minute demo video]

## Team

- Built at Hack@Brown 2026
