# Cognitive Weave

Cognitive Weave is an innovative project that implements a proactive, LLM-driven synthesis of new, structured insights (Insight Aggregates) from enriched information units (Insight Particles), aiming for a more dynamic and emergent understanding within the agent's memory.

## Authors

- **Mohith Suresh**
  - Affiliation: University of Southern California
  - Email: mohiths@usc.edu

- **Priyam**
  - Email: psharma2@mail.yu.edu

- **Sparsh Gupta**
  - Affiliation: University of Southern California
  - Email: sparshg@usc.edu

- **Yuvraj Anupam Chauhan**
  - Affiliation: Northeastern University
  - Email: chauhan.yuv@northeastern.edu

## Project Overview

Cognitive Weave introduces a novel approach to information processing and memory management in AI systems. The core components include:

1. **Insight Particles (IPs)**: Fundamental units of knowledge that include:
   - Resonance keys (core identifying terms)
   - Signifiers (broader categorical labels)
   - Situational imprint (concise contextual summary)
   - Extracted entities

2. **Insight Aggregates (IAs)**: Higher-level synthesized knowledge created from related IPs
3. **Semantic Oracle Interface (SOI)**: LLM-powered interface for deep semantic understanding
4. **Spatio-Temporal Resonance Graph (STRG)**: Hybrid data structure for multi-faceted recall

## Completed Tasks

- [x] Basic project structure setup
- [x] Implementation of core data structures (InsightParticle, InsightAggregateAttributes)
- [x] Azure OpenAI integration setup
- [x] Semantic Oracle Interface implementation
- [x] Basic logging and error handling
- [x] Demo conversation agent implementation
- [x] IP enrichment functionality
- [x] IA synthesis from imprints

## To-Do Tasks

- [ ] Implement full STRG (Spatio-Temporal Resonance Graph) structure
- [ ] Add comprehensive test suite
- [ ] Implement memory persistence layer
- [ ] Add support for multiple LLM providers
- [ ] Enhance IA synthesis with more sophisticated algorithms
- [ ] Add visualization tools for memory structure
- [ ] Implement advanced retrieval mechanisms
- [ ] Add support for multi-modal inputs
- [ ] Create detailed API documentation
- [ ] Performance optimization for large-scale deployments
- [ ] Add security features and access control
- [ ] Create user interface for memory visualization
- [ ] Implement memory cleanup and optimization routines

## Setup

1. Clone the repository
2. Configure Azure OpenAI credentials in `cognitive_weave/utils.py`
3. Install dependencies (requirements.txt to be added)
4. Run the demo conversation agent using `python main.py`

## Project Structure

```
cognitive-weave/
├── cognitive_weave/
│   ├── __init__.py
│   ├── data_structures.py
│   ├── semantic_oracle.py
│   └── utils.py
├── example_conversations/
│   ├── demo.py
│   └── info.md
└── main.py
```

## Contributing

Please contact any of the authors for contribution guidelines and to get involved in the project.

## License

TBD - License information to be added. 