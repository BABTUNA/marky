# AdVantage — Agent Orchestration Flowchart

Orchestration flow for the full AdVantage pipeline with **parallel research** and dual output (storyboard + viral).

> **To generate the PNG:** Paste the Mermaid block below into [mermaid.live](https://mermaid.live) and export as PNG. Save as `docs/agent_orchestration.png`.

---

## Full Orchestration Chain (with Parallel Research)

```mermaid
flowchart TB
    subgraph Entry[" "]
        A[User / ASI:One]
        B[Orchestrator]
        C[Intent Extractor]
    end

    subgraph Research["Research Layer - Parallel Execution"]
        direction TB
        RSTART[Research]
        RSTART --> LI[Local Intel]
        RSTART --> RI[Review Intel]
        RSTART --> YI[Yelp Intel]
        RSTART --> GI[Google Trends]
        RSTART --> RQ[Related Questions]
        LI --> RSYNTH
        RI --> RSYNTH
        YI --> RSYNTH
        GI --> RSYNTH
        RQ --> RSYNTH
        RSYNTH[Research Synthesis + Competitor Map]
    end

    subgraph Content["Content Creation"]
        L[Location Scout]
        T[Trend Analyzer]
        S[Script Writer]
    end

    subgraph Storyboard["Storyboard Package"]
        I[Image Generator]
        VA[Video Assembly]
    end

    subgraph ViralPkg["Viral Video Package"]
        VEO[VEO 3]
        LYR[Lyria]
        VIRAL_ASM[Viral Assembler]
    end

    subgraph Assembly["Campaign Assembly"]
        COST[Cost Estimator]
        SOC[Social Media]
        PDF[PDF Builder]
    end

    subgraph Output[" "]
        U[Upload]
        RES[Thumbnail + Links]
    end

    A --> B
    B --> C
    C --> RSTART
    RSYNTH --> L
    L --> T
    T --> S
    S --> I
    S --> VEO
    I --> VA
    VEO --> LYR
    LYR --> VIRAL_ASM
    VA --> COST
    VIRAL_ASM --> COST
    COST --> SOC
    SOC --> PDF
    PDF --> U
    U --> RES
    RES --> A
```

---

## Pipeline Variants

| Pipeline           | Agents                                                                 |
|--------------------|------------------------------------------------------------------------|
| **storyboard_video** (default) | research → location_scout → trend_analyzer → script_writer → image_generator → video_assembly → cost_estimator → social_media → pdf_builder |
| **viral_video**    | research → trend_analyzer → script_writer → veo3_generator → lyria_music → viral_video_assembler |
| script             | research → location_scout → trend_analyzer → script_writer             |
| storyboard         | research → location_scout → trend_analyzer → script_writer → image_generator |
| pdf                | research → trend_analyzer → script_writer → image_generator → cost_estimator → location_scout → pdf_builder |
| quick_test         | script_writer → image_generator → video_assembly → cost_estimator → social_media → pdf_builder |

---

## Files

| File | Purpose |
|------|---------|
| `docs/agent_orchestration.mmd` | Mermaid source (parallel research + dual output) |
| `docs/agent_flowchart.mmd` | Legacy sequential flowchart |

**Generate PNG:** Paste Mermaid into [mermaid.live](https://mermaid.live) → Export → PNG
