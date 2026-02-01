# AdBoard AI — Agent Orchestration Flowchart

Orchestration flow for the **confirmed storyboard_video pipeline**.

> Run `npx -y @mermaid-js/mermaid-cli mmdc -i docs/agent_flowchart.mmd -o docs/agent_flowchart.png` to generate the diagram image.

---

## Main Pipeline (storyboard_video)

```mermaid
flowchart TB
    subgraph Entry
        A[User / ASI:One Chat]
        B[Orchestrator]
        C[Intent Extractor]
    end

    subgraph Pipeline["AdBoard Pipeline (Sequential)"]
        R[1. Research<br/>Marky: LocalIntel, Reviews, Trends]
        L[2. Location Scout<br/>Google Places]
        T[3. Trend Analyzer<br/>Viral patterns, hooks]
        S[4. Script Writer<br/>Scene breakdown]
        I[5. Image Generator<br/>Imagen 3 storyboard frames]
        V[6. Video Assembly<br/>Ken Burns animation]
        C2[7. Cost Estimator<br/>Budget breakdown]
        SM[8. Social Media<br/>Hashtags, captions]
        P[9. PDF Builder<br/>Campaign package + map]
    end

    subgraph Output
        U[Upload: Drive / tmpfiles]
        F[Format Results]
        RES[Response: Thumbnail + Links]
    end

    A --> B
    B --> C
    C --> R
    R --> L
    L --> T
    T --> S
    S --> I
    I --> V
    V --> C2
    C2 --> SM
    SM --> P
    P --> U
    U --> F
    F --> RES
    RES --> A
```

---

## Research Sub-Flow (Marky)

```mermaid
flowchart LR
    subgraph Marky["Research Agent (Marky Workflow)"]
        LI[Local Intel<br/>SerpAPI, competitor discovery]
        RI[Review Intel<br/>Google Reviews]
        YI[Yelp Intel<br/>Yelp reviews]
        GI[Google Trends<br/>Keyword trends]
        RQ[Related Questions<br/>People also ask]
    end

    subgraph Output2["Research Output"]
        MAP[Competitor Map<br/>Google Static Maps]
        DATA[Unified research data]
    end

    LI --> DATA
    RI --> DATA
    YI --> DATA
    GI --> DATA
    RQ --> DATA
    DATA --> MAP
```

---

## Pipeline Variants

| Pipeline           | Agents                                                                 |
|--------------------|------------------------------------------------------------------------|
| **storyboard_video** (default) | research → location_scout → trend_analyzer → script_writer → image_generator → video_assembly → cost_estimator → social_media → pdf_builder |
| script             | research → location_scout → trend_analyzer → script_writer             |
| storyboard         | research → location_scout → trend_analyzer → script_writer → image_generator |
| pdf                | research → trend_analyzer → script_writer → image_generator → cost_estimator → location_scout → pdf_builder |
| quick_test         | script_writer → image_generator → video_assembly → cost_estimator → social_media → pdf_builder |

---

## Rendered Diagram

If you have Node.js, generate the PNG:

```bash
npx -y @mermaid-js/mermaid-cli mmdc -i docs/agent_flowchart.mmd -o docs/agent_flowchart.png
```

Otherwise, paste the Mermaid block from above into [mermaid.live](https://mermaid.live) and export as PNG/SVG.
