---
title: "Kiro is Finally GA: My Three Favorite Features"
date: 2025-11-17T00:00:00-05:00
draft: false
---

After months in preview, Kiro is finally generally available. If you haven't heard of it yet, Kiro is an AI-powered development tool (both IDE and CLI) built on Claude that brings spec-driven development to AI coding. I've been taking it for a spin while in preview, and now that it's generally available, I wanted to share the three features that standout from other tools like Claude Code and Cursor.

## Property-Based Testing 

You may have already fallen into the vibe coding trap of blindly trusting AI-generated code without testing it thoroughly. Kiro's property-based testing solves this by measuring what they call "spec correctness" - whether the code actually matches the behavior you defined in your specification.

The magic happens in a few steps. First, you write specs with acceptance criteria - Kiro helps with this during the spec writing process. From those specs, Kiro extracts *properties*: universal statements that must hold true for a range of inputs, not just single examples.

For instance, if you're building a traffic light controller, a property might be: "for any sequence of operations (state transitions, emergency mode activation, timing updates), at most one direction should have a green signal." Notice the "for any" - that's the key difference from traditional unit tests that only check specific examples.

Under the hood, Kiro uses [Hypothesis](https://hypothesis.readthedocs.io/) to turn these properties into executable tests. It generates 100+ random test cases automatically, trying to violate your properties. This catches edge cases that you and the AI would never think to test manually.

When a property fails, the **shrinking** technique kicks in. Instead of showing you a complex failing input with tons of noise, it systematically simplifies the counterexample to reveal the minimal case that triggers the bug. For example, if your test fails on a complex tree structure with dozens of nodes, shrinking might reduce it to just two single-node trees - instantly revealing the core issue (maybe your union operation doesn't handle duplicates).

Common property patterns Kiro recognizes:

- **Runtime invariants**: Data structures maintaining conditions (like "balance factor is always between -1 and 1" for AVL trees)
- **Round-trip properties**: Encode then decode should return the original (serialization/parsing)
- **Idempotent operations**: Running twice equals running once (like DELETE requests)

This is the first AI tool I've used that doesn't just generate code and hope for the best. It actively tries to break what it built and shows you where the spec and implementation diverge. The flow is: `Spec → Properties → Executable tests → Counterexamples → Fixes`. If you're someone who already uses SDLC methodologies like Behavior-Driven Development (BDD) and Test Driven Development (TDD), this adds another confidence layer on top.

I actually trust the code Kiro generates now. Do I still review it? Yes (and so should you), but I trust it more than before. It's not just passing the happy path tests - it's been tested against scenarios I didn't even know existed. When shrinking hands me a minimal failing case, debugging becomes trivial. When it passes property-based testing, I can ship my code with a higher degree of confidence.

## Checkpointing

Before checkpointing shipped, I was making sure each new iteration of my code was on a fresh Git commit so I could roll back easily if my AI minions went sideways.

Kiro's checkpointing is more than just version control though - it's what makes AI-assisted development feel like a conversation instead of a series of risky transactions.

Checkpoints happen automatically before each task starts - no configuration needed. Visual markers appear in your chat interface showing where each checkpoint was created. When you restore a checkpoint, you get back both the file state AND the full conversation context up to that point. Even messages you typed but didn't send yet stay in your chat box.

Here's the key difference from Git: checkpointing only tracks files that Kiro modified in your current session. It's not a full codebase snapshot - it's specifically about reverting AI-generated changes while preserving the conversational flow that led there.

The restore is simple: click the checkpoint line, hit restore, and you're back. The entire state of any file Kiro touched gets reverted to that exact moment.

It fundamentally changes my mindset. With Git, reverting means losing the conversational context - you have to re-explain everything. With checkpointing, I keep the full context of what we were trying and why. This means I can let Kiro take bigger swings on complex refactors with LESS fear than before.

Real examples where this shines:
- **Exploring implementations**: You want to build an API endpoint but not sure between REST or GraphQL? Try REST, test it, restore, then try GraphQL. Same conversation, different approach, zero manual cleanup.
- **Recovering from misunderstandings**: You asked for "authentication" and Kiro built OAuth2, but you meant simple API keys? Restore the checkpoint, clarify your requirement, and Kiro tries again with the right approach.
- **Safe experimentation**: Want to refactor for performance? Try it, run benchmarks, and restore if the results aren't good. No harm, no foul.

The workflow becomes: `try → evaluate → restore → try again`. Each iteration builds on lessons learned without the baggage of failed attempts cluttering your code.

I get derailed by mistakes less so than before. More importantly, I spend less mental energy on "what if this goes wrong" and more on "what if this goes right." No wasted credits on cleanup conversations. No reconstructing context after manually reverting files. Just rapid iteration with full confidence.  This is fantastic for rapid prototyping and experimentation.

## Kiro CLI (formerly Amazon Q CLI) with Custom Agents

I live in the terminal (#vim-master-race). So having to context-switch to an IDE to use AI tools breaks my workflow completely. The Kiro CLI changes that, but it's not just "Kiro, but in your terminal." The real innovation is custom agents - specialized AI assistants built from simple configuration files.

Installation is one command: `curl -fsSL https://cli.kiro.dev/install | bash` (macOS/Linux).  Then, you can chat with the general agent or create custom ones.

Custom agents are defined in JSON config files that specify:
- **Name and description**: What the agent does
- **Specialized prompt**: Defines the agent's expertise (e.g., "You are a frontend developer specializing in React, TypeScript, and modern frontend tooling. You build type-safe applications using TanStack Query for data fetching, TanStack Router for routing, and Vite for the build system.")
- **Allowed tools**: Pre-approved tools (file read/write, bash execution, etc.) so you're not constantly approving permissions.
- **Tool settings**: File path restrictions per tool - your frontend agent can only modify `src/components/**` and `src/hooks/**`
- **Resources**: Auto-loaded context files with project standards and documentation (like Steering docs, code style guides, and design patterns)

Here's what makes this architecture powerful: the agent configuration lives in your `.kiro` folder and works identically in both the CLI and IDE. Configure once, use everywhere.

A general purpose agent wastes context window space considering backend patterns, DevOps concerns, and other irrelevant topics. It has to reason about your entire codebase even though you only need help with one part. You have to constantly re-explain project structure and coding standards.  Custom agents helps make this process more efficient by focusing the agent down to its core responsibilities.

Here's a more detailed example configuration for a frontend specialist:

```json
{
  "name": "frontend-specialist",
  "description": "Expert in building React applications with TanStack Query, TanStack Router, TypeScript, and Vite",
  "prompt": "You are a frontend developer specializing in React, TypeScript, and modern frontend tooling. You build type-safe applications using TanStack Query for data fetching, TanStack Router for routing, and Vite for the build system. You write clean, performant components with proper error boundaries, loading states, and TypeScript types. You follow React best practices including proper hook usage, component composition, and avoiding prop drilling.",
  "tools": ["fs_read", "fs_write", "execute_bash"],
  "toolsSettings": {
    "fs_write": {
      "allowedPaths": [
        "src/components/**",
        "src/routes/**",
        "src/hooks/**",
        "src/lib/**",
        "src/types/**",
        "src/App.tsx",
        "vite.config.ts",
        "package.json"
      ]
    }
  },
  "resources": [
    "file://.kiro/steering/frontend-standards.md", // add your steering docs to provide guidance on best practices and patterns for frontend development.
    "file://.kiro/steering/component-patterns.md"
  ]
}
```

With this configuration:
- The frontend specialist only thinks about React components, TanStack Query patterns, and routing logic
- File path restrictions prevent it from touching backend API code or infrastructure files
- Resource files automatically load your component patterns and frontend standards
- Persistent context across sessions - no re-explaining the basics

Use your custom agent:

```bash
kiro-cli chat --agent frontend-specialist
```

Then you can ask things like:
- "Create a new route at `/dashboard` using TanStack Router with a loader that fetches user stats using TanStack Query. Include loading and error states."
- "I'm getting a type error in my query hooks. Help me properly type the TanStack Query response for the user profile endpoint."
- "Build a data table component that uses TanStack Query for pagination and sorting, with proper TypeScript types and loading skeletons."

The agent knows your React patterns, understands your TanStack Query setup, and consistently follows your component architecture - because they're loaded from resource files automatically. It never suggests Express routes or Docker configs because those files are off-limits.

You work faster because you're not context-switching between terminal and IDE. You get better results because each agent has a narrow, well-defined domain. No wasted tokens on irrelevant context. No permission fatigue from constant approval prompts. No explaining the same standards repeatedly.

The efficiency gains are measurable too - Kiro's Auto agent (which dynamically picks the optimal model) is 30% more cost-efficient than always using Claude Sonnet 4, saving credits while maintaining quality.

## Honorable Mentions

- **Multi-root workspace support**: Finally, proper monorepo and git submodule support. Work across multiple project roots simultaneously.  I've already been doing this with the `/add-dir` command in Claude Code, so this is a welcome addition!
- **Kiro for Organizations**: AWS IAM Identity Center integration, centralized management, team billing. If you're on a team, this is huge as it enables org-wide billing and cost control as well as usage observability.

## Getting Started

If you want to try Kiro:
- **Free tier**: 50 perpetual credits (enough to get a real feel for it)
- **New user bonus**: 500 credits for 30 days
- **Startup offer**: If you're at a startup (up to Series B), you can get a full year of Pro+ for free (until Dec 31, 2025)
- **CLI install**: `curl -fsSL https://cli.kiro.dev/install | bash` (macOS/Linux)
- **IDE install**: [Download for your OS here](https://kiro.dev/downloads/)
