# AI Analytics Copilot

## Building a Production-Grade AI Analytics Platform — One Level at a Time

**AI Analytics Copilot** is a progressive engineering project that demonstrates how to evolve an AI-powered analytics system from an initial prototype into a production-oriented platform with retrieval, model routing, agent orchestration, guardrails, observability, evaluation, and controlled AI execution.

The project is deliberately developed in **levels**.

Each level represents a significant architectural capability and is documented independently so that the evolution of the platform can be understood, reproduced, tested, and extended.

---

## 🎯 Project Objective

The objective of this project is to build an **AI Analytics Copilot** capable of answering questions about software repositories and analytics data while demonstrating the engineering disciplines required for production AI systems.

The project explores the progression from:

**Data → Retrieval → RAG → Model Routing → Agents → Control → Evaluation → Production Intelligence**

Rather than presenting AI as a single application or a single model call, the project demonstrates how the surrounding engineering architecture evolves to provide:

- Reliable retrieval
- Multiple LLM providers
- Model routing
- Agent-based execution
- Tool integration
- Guardrails
- Structured outputs
- Execution traces
- Evaluation and replay
- Observability
- Controlled multi-step workflows
- Production-oriented AWS integration

The goal is not simply to make an AI application work.

The goal is to demonstrate **how to engineer an AI system that can be understood, evaluated, observed, controlled, and progressively hardened for production**.

---

## 🏗️ Project Repository

The complete project is available on GitHub:

**https://github.com/eyespan/ai-analytics-copilot/**

The repository contains the implementation, infrastructure, deployment configuration, tests, and detailed design documentation for each development level.

---

# 📚 Development Levels

The project is intentionally structured as a sequence of levels.

Each level builds on the capabilities established previously.

The detailed design documents in the repository explain the architecture, objectives, implementation decisions, components, testing approach, and progression for each level.

> **Important:** The level design documents are the authoritative guide to the architecture and objectives of each stage.

A typical progression is:

```text
Level 1
   ↓
Level 2
   ↓
Level 3
   ↓
Level 4
   ↓
Level 5
   ↓
Level 6
   ↓
Level 7
```

The exact implementation and scope of each level can be found in its corresponding design document in the repository.

---

# 🔎 Exploring the Levels

Visit the repository:

**https://github.com/eyespan/ai-analytics-copilot/**

Then explore the level-specific design documentation.

Look for the corresponding:

```text
DESIGN_LEVEL1.md
DESIGN_LEVEL2.md
DESIGN_LEVEL3.md
...
DESIGN_LEVEL7.md
```

and the associated README documentation where provided.

These documents describe **why** each level exists, **what** is introduced, and **how** the architecture evolves.

---

# 🧭 How the Project Evolves

The project follows a progressive architecture rather than attempting to implement every capability from the beginning.

The broad progression is:

### Early Levels — Foundation

The early stages establish the application and data foundations required by the platform.

Typical concerns include:

- Application structure
- Data ingestion
- Data storage
- Repository data
- Initial APIs
- Initial user interaction

### Retrieval and RAG

The retrieval stages introduce the knowledge retrieval layer.

The architecture evolves towards:

```text
User Query
    ↓
API
    ↓
Retrieval
    ↓
Ranking / Reranking
    ↓
LLM
    ↓
Answer
```

### Model Routing

The routing stages introduce the ability to select an LLM provider/model according to the request and configured policy.

The architecture becomes:

```text
Query
  ↓
Model Router
  ↓
Routing Policy
  ├── Ollama
  ├── AWS Bedrock
  └── Other supported providers
```

AWS Bedrock is integrated as a supported provider while preserving the existing routing architecture.

The project can therefore demonstrate local development using Ollama while also supporting a production-oriented AWS Bedrock path when the AWS environment permits it.

### Agent Orchestration

The later levels introduce controlled agent execution.

A simplified flow becomes:

```text
User Request
     ↓
Planner
     ↓
Execution Plan
     ↓
Tool Execution
     ↓
Verification / Repair
     ↓
Final Answer
```

The objective is to move from simple LLM responses towards controlled execution workflows.

### Level 6 — Production Intelligence & Control

Level 6 focuses on the production control layer.

The architecture introduces capabilities such as:

- Guardrails
- Structured outputs
- Tool validation
- Tool permissions
- Execution tracing
- Evaluation pipelines
- Replay
- Deterministic evaluation
- Production-oriented model execution
- Controlled agent workflows

The emphasis is on making AI execution **observable, testable, and controlled**.

### Level 7 — Production Configuration and Provider Choice

Level 7 builds on the Level 6 control architecture without replacing it.

One of the important capabilities introduced in the Level 7 evolution is the ability to configure the preferred LLM provider while retaining the existing routing and orchestration architecture.

The platform can support configuration such as:

```text
LLM Provider
├── Ollama
└── AWS Bedrock

Fallback
└── Enabled / Disabled
```

The intention is to separate **provider configuration** from the core orchestration, evaluation, tracing, and control mechanisms.

---

# 🧪 Testing Each Level

Each level should be treated as an independently understandable milestone.

When exploring a level:

1. Read the design document.
2. Read the level README.
3. Check out the relevant code/state.
4. Deploy the required infrastructure.
5. Run the documented tests.
6. Inspect application behaviour.
7. Inspect traces and evaluation results where applicable.
8. Compare the implementation with the corresponding design document.

This makes the repository useful both as a working project and as an architectural learning resource.

---

# 🍴 Forking the Project

You are encouraged to fork the repository and experiment with the different levels.

Fork it from GitHub, then clone your fork:

```bash
git clone https://github.com/<your-github-user>/ai-analytics-copilot.git
cd ai-analytics-copilot
```

You can then work through the levels progressively.

---

# 🧩 Working With a Specific Level

If you want to study or extend a particular level, the recommended approach is:

```text
1. Read DESIGN_LEVELX.md
          ↓
2. Read the corresponding README
          ↓
3. Check out the relevant project state
          ↓
4. Deploy / run the level
          ↓
5. Execute the documented tests
          ↓
6. Modify and experiment
```

Replace `X` with the level you want to investigate.

For example:

```text
Level 4
Level 5
Level 6
Level 7
```

This allows you to understand how the platform changed rather than seeing only the final implementation.

---

# 🌿 Experimenting Safely

A useful way to experiment is to create your own branch:

```bash
git checkout -b my-experiment
```

Make your changes, test them, and compare the result with the corresponding level design.

For example:

```bash
git diff
```

This makes it possible to understand exactly how your implementation differs from the documented architecture.

---

# 🏛️ Architecture Philosophy

The project follows several principles throughout its evolution.

### Progressive Complexity

Capabilities are introduced when they become architecturally useful rather than attempting to build the entire platform at once.

### Separation of Concerns

The system separates major responsibilities such as:

- Retrieval
- Model routing
- Model execution
- Agent orchestration
- Tool execution
- Guardrails
- Evaluation
- Observability
- Storage

### Provider Independence

The orchestration layer should not be tightly coupled to one LLM provider.

The routing layer determines which provider/model is appropriate, while the orchestration system continues to operate around that decision.

### Observability

AI execution should produce evidence of what happened.

Where implemented, traces record events such as:

```text
Retrieval
Model Routing
Planning
Tool Execution
Repair
Final Answer
```

### Evaluation

The system should not rely solely on subjective inspection of model output.

Evaluation capabilities are introduced to compare expected and actual execution behaviour.

### Controlled Autonomy

Agents should operate within explicit boundaries.

The project therefore emphasizes:

- Maximum execution steps
- Tool validation
- Guardrails
- Structured execution plans
- Validation
- Repair
- Traceability
- Deterministic evaluation

---

# ☁️ AWS and Production-Oriented Development

AWS technologies are progressively introduced as the project moves towards production-oriented architecture.

AWS Bedrock is supported as an LLM provider in the model-routing architecture.

The ability to use Bedrock depends on the AWS environment in which the project is deployed.

An AWS organization may restrict Bedrock through permissions or Service Control Policies.

That does not prevent the architecture from supporting Bedrock; it means the provider cannot be invoked in an environment where the required permissions are unavailable.

This distinction is important:

```text
Architecture supports Bedrock
             ≠
Every AWS account permits Bedrock execution
```

The project therefore retains Ollama as a useful local/testing provider while providing an AWS Bedrock integration path for suitable environments.

---

# 🔬 What You Can Learn From the Project

This project is intended to demonstrate more than the final application.

By following the levels, you can explore questions such as:

- How should repository data be indexed for AI retrieval?
- How does a RAG system evolve?
- How should multiple LLM providers be abstracted?
- How can model routing be separated from orchestration?
- How should an agent create and execute a plan?
- How can tool execution be validated?
- How can AI execution be traced?
- How can an agent workflow be evaluated?
- How can evaluation results be replayed?
- How should guardrails fit around an agent system?
- How can local models and managed cloud models coexist?
- What changes when moving an AI prototype towards production?

---

# 🚀 Getting Started

Start with the repository:

**https://github.com/eyespan/ai-analytics-copilot/**

Then:

```text
Clone / Fork
    ↓
Choose a Level
    ↓
Read its Design Document
    ↓
Read its README
    ↓
Deploy
    ↓
Test
    ↓
Inspect
    ↓
Experiment
```

Do not jump directly to the final level if your objective is to understand the architecture.

The value of the project is in seeing **how the system evolves**.

---

# 🤝 Contributing and Experimenting

The repository is intended to be useful for experimentation and learning.

You can:

- Fork the repository
- Create feature branches
- Experiment with individual levels
- Replace components
- Add new model providers
- Extend routing policies
- Add evaluation datasets
- Improve observability
- Experiment with different retrieval strategies
- Extend agent tools
- Compare local and cloud LLM execution

When making substantial architectural changes, compare them against the relevant level design document so that the architectural intent remains clear.

---

# 📖 Documentation

The detailed documentation lives in the GitHub repository:

**https://github.com/eyespan/ai-analytics-copilot/**

Start with the level-specific design documents:

```text
DESIGN_LEVEL1.md
DESIGN_LEVEL2.md
DESIGN_LEVEL3.md
DESIGN_LEVEL4.md
DESIGN_LEVEL5.md
DESIGN_LEVEL6.md
DESIGN_LEVEL7.md
```

Where available, also review:

```text
README_LEVEL1.md
README_LEVEL2.md
README_LEVEL3.md
README_LEVEL4.md
README_LEVEL5.md
README_LEVEL6.md
README_LEVEL7.md
```

The documentation is deliberately separated by level so that each architectural milestone can be studied independently.

---

# ⭐ Project

If you find the project useful, consider starring the repository:

**https://github.com/eyespan/ai-analytics-copilot/**

---

## Final Perspective

AI systems become significantly more interesting when the challenge moves beyond:

> "Can the model answer the question?"

and becomes:

> "Can we build a system around the model that is reliable, observable, controllable, testable, evaluable, and capable of evolving towards production?"

**AI Analytics Copilot** is an exploration of that journey.

The individual levels provide the roadmap.

The design documents explain the architecture.

The repository contains the implementation.

And the ability to fork the project allows you to build your own version of the journey.

---

**Repository:** https://github.com/eyespan/ai-analytics-copilot/

**Start here:** Fork the repository → choose a level → read its design document → deploy → test → experiment.
