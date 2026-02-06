

What is Spec-Driven Development?
Spec-Driven Development flips the script on traditional software development. For
decades, code has been king — specifications were just scaffolding we built and
discarded once the "real work" of coding began. Spec-Driven Development changes
this: specifications become executable, directly generating working implementations
rather than just guiding them.

## Get Started
- Install Specify CLI
Choose your preferred installation method:

Option 1: Persistent Installation (Recommended)
Install once and use everywhere:

# From PyPI (recommended)
pip install specifyplus

# Or with uv tools
uv tool install specifyplus

# Upgrade to latest later
pip install -U specifyplus
uv tool upgrade specifyplus
You may uninstall specifyplus:

pip uninstall specifyplus

# or

uv tool uninstall specifyplus
Then use the tool directly:

# Create new project
specifyplus init <PROJECT_NAME>
# or
sp init <PROJECT_NAME>

# Or initialize in existing project
specifyplus init . --ai claude
# or
sp init --here --ai claude


# Check installed tools
specifyplus check
# or
sp check
To upgrade Specify, see the Upgrade Guide for detailed instructions. Quick upgrade:

uv tool install specify-cli --force --from git+https://github.com/github/spec-kit.git
## Option 2: One-time Usage
Run directly without installing:

uvx specifyplus --help
uvx specifyplus init <PROJECT_NAME>
# or
uvx sp init <PROJECT_NAME>
Benefits of persistent installation:

Tool stays installed and available in PATH
No need to create shell aliases
Better tool management with uv tool list, uv tool upgrade, uv tool uninstall
Cleaner shell configuration
- Establish project principles
Use the /sp.constitution command to create your project's governing principles and
development guidelines that will guide all subsequent development.

/sp.constitution Create principles focused on code quality, testing standards, user
experience consistency, and performance requirements
- Create the spec
Use the /sp.specify command to describe what you want to build. Focus on the what
and why, not the tech stack.

/sp.specify Build an application that can help me organize my photos in separate photo
albums. Albums are grouped by date and can be re-organized by dragging and dropping
on the main page. Albums are never in other nested albums. Within each album, photos
are previewed in a tile-like interface.
- Create a technical implementation plan
Use the /sp.plan command to provide your tech stack and architecture choices.

/sp.plan The application uses Vite with minimal number of libraries. Use vanilla HTML,
CSS, and JavaScript as much as possible. Images are not uploaded anywhere and
metadata is stored in a local SQLite database.

- Break down into tasks
Use /sp.tasks to create an actionable task list from your implementation plan.

## /sp.tasks
- Execute implementation
Use /sp.implement to execute all tasks and build your feature according to the plan.

## /sp.implement
For detailed step-by-step instructions, see our comprehensive guide.

## Video Overview
Want to see Spec Kit in action? Watch our video overview!

Spec Kit video header

Supported AI Agents
## Agent Support Notes
Qoder CLI
Amazon Q Developer CLI     Amazon Q Developer CLI does not support custom
arguments for slash commands.
## Amp
Auggie CLI
## Claude Code
CodeBuddy CLI
Codex CLI
## Cursor
Gemini CLI
GitHub Copilot
IBM Bob    IDE-based agent with slash command support
## Jules
## Kilo Code
opencode
## Qwen Code
## Roo Code
SHAI (OVHcloud)
## Windsurf
Specify CLI Reference
Learning subagents (optional)

Spec Architect – docs-
plus/02_start_prompting/02_qwen_code/04_subagents/prompts/0002-spec-
architect.prompt.md
PHR/ADR Curator & Evaluator – docs-
plus/02_start_prompting/02_qwen_code/04_subagents/prompts/0004-phr-adr-
curator.prompt.md
Note: Use specifyplus or sp commands instead of specify in this fork.

The specify command supports the following options:

## Commands
## Command Description
init Initialize a new Specify project from the latest template
check Check for installed tools (git, claude, gemini, code/code-insiders, cursor-agent,
windsurf, qwen, opencode, codex, shai, qoder)
version Display version and system information
specifyplus init Arguments & Options
Argument/Option Type Description
<project-name> Argument Name for your new project directory (optional if
using --here, or use . for current directory)
--ai Option AI assistant to use: claude, gemini, copilot, cursor-agent, qwen,
opencode, codex, windsurf, kilocode, auggie, roo, codebuddy, amp, shai, q, bob, or
qoder
--script Option Script variant to use: sh (bash/zsh) or ps (PowerShell)
--ignore-agent-tools Flag Skip checks for AI agent tools like Claude Code
--no-git Flag Skip git repository initialization
--here Flag Initialize project in the current directory instead of creating a new one
--force Flag Force merge/overwrite when initializing in current directory (skip
confirmation)
--skip-tls Flag Skip SSL/TLS verification (not recommended)
--debug Flag Enable detailed debug output for troubleshooting
--github-token Option GitHub token for API requests (or set
GH_TOKEN/GITHUB_TOKEN env variable)
## Examples
# Basic project initialization
specifyplus init my-project

# Initialize with specific AI assistant
specifyplus init my-project --ai claude

# Initialize with Cursor support

specifyplus init my-project --ai cursor

# Initialize with Qoder support
specify init my-project --ai qoder

# Initialize with Windsurf support
specifyplus init my-project --ai windsurf

# Initialize with Amp support
specify init my-project --ai amp

# Initialize with SHAI support
specify init my-project --ai shai

# Initialize with IBM Bob support
specify init my-project --ai bob

# Initialize with PowerShell scripts (Windows/cross-platform)
specifyplus init my-project --ai copilot --script ps

# Initialize in current directory
specifyplus init . --ai copilot
# or use the --here flag
specifyplus init --here --ai copilot

# Force merge into current (non-empty) directory without confirmation
specifyplus init . --force --ai copilot
# or
specifyplus init --here --force --ai copilot

# Skip git initialization
specifyplus init my-project --ai gemini --no-git

# Enable debug output for troubleshooting
specifyplus init my-project --ai claude --debug

# Use GitHub token for API requests (helpful for corporate environments)
specifyplus init my-project --ai claude --github-token ghp_your_token_here

# Check system requirements
specifyplus check

## Available Slash Commands
After running specifyplus init, your AI coding agent will have access to these slash
commands for structured development:

## Core Commands
Essential commands for the Spec-Driven Development workflow:

## Command Description
/sp.constitution Create or update project governing principles and development
guidelines
/sp.specify Define what you want to build (requirements and user stories)
/sp.plan Create technical implementation plans with your chosen tech stack
/sp.tasks Generate actionable task lists for implementation
/sp.implement Execute all tasks to build the feature according to the plan
## Optional Commands
Additional commands for enhanced quality and validation:

## Command Description
/sp.clarify Clarify underspecified areas (recommended before /sp.plan; formerly
## /quizme)
/sp.analyze Cross-artifact consistency & coverage analysis (run after /sp.tasks,
before /sp.implement)
/sp.checklist Generate custom quality checklists that validate requirements
completeness, clarity, and consistency (like "unit tests for English")
## Environment Variables
## Variable Description
SPECIFY_FEATURE Override feature detection for non-Git repositories. Set to the
feature directory name (e.g., 001-photo-albums) to work on a specific feature when not
using Git branches.
**Must be set in the context of the agent you're working with prior to using /sp.plan or
follow-up commands.
## Core Philosophy
Spec-Driven Development is a structured process that emphasizes:

Intent-driven development where specifications define the "what" before the "how"
Rich specification creation using guardrails and organizational principles
Multi-step refinement rather than one-shot code generation from prompts
Heavy reliance on advanced AI model capabilities for specification interpretation
## Development Phases
## Phase Focus Key Activities

0-to-1 Development ("Greenfield") Generate from scratch
Start with high-level requirements
Generate specifications
Plan implementation steps
Build production-ready applications
Creative Exploration Parallel implementations
Explore diverse solutions
Support multiple technology stacks & architectures
Experiment with UX patterns
Iterative Enhancement ("Brownfield") Brownfield modernization
Add features iteratively
Modernize legacy systems
Adapt processes
## Experimental Goals
Our research and experimentation focus on:

Technology independence
Create applications using diverse technology stacks
Validate the hypothesis that Spec-Driven Development is a process not tied to specific
technologies, programming languages, or frameworks
Enterprise constraints
Demonstrate mission-critical application development
Incorporate organizational constraints (cloud providers, tech stacks, engineering
practices)
Support enterprise design systems and compliance requirements
User-centric development
Build applications for different user cohorts and preferences
Support various development approaches (from vibe-coding to AI-native development)
Creative & iterative processes
Validate the concept of parallel implementation exploration
Provide robust iterative feature development workflows
Extend processes to handle upgrades and modernization tasks
## Prerequisites
Linux/macOS/Windows
Supported AI coding agent.
uv for package management
## Python 3.11+
## Git
If you encounter issues with an agent, please open an issue so we can refine the
integration.


## Learn More
Complete Spec-Driven Development Methodology - Deep dive into the full process
Detailed Walkthrough - Step-by-step implementation guide
## Detailed Process
Click to expand the detailed step-by-step walkthrough
## Troubleshooting
Git Credential Manager on Linux
If you're having issues with Git authentication on Linux, you can install Git Credential
## Manager:

#!/usr/bin/env bash
set -e
echo "Downloading Git Credential Manager v2.6.1..."
wget https://github.com/git-ecosystem/git-credential-
manager/releases/download/v2.6.1/gcm-linux_amd64.2.6.1.deb
echo "Installing Git Credential Manager..."
sudo dpkg -i gcm-linux_amd64.2.6.1.deb
echo "Configuring Git to use GCM..."
git config --global credential.helper manager
echo "Cleaning up..."
rm gcm-linux_amd64.2.6.1.deb