# macOS-use Custom

[![GitHub stars](https://img.shields.io/github/stars/MihiroH/macOS-use-custom?style=social)](https://github.com/MihiroH/macOS-use-custom/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<div align="center">
  <h2>Tell your MacBook what to do, and it's done—across ANY app.</h2>
  <p>A customized version of macOS-use with enhanced Claude CLI integration</p>
  <p><em>Based on the original work by <a href="https://github.com/browser-use/macOS-use">browser-use/macOS-use</a></em></p>
</div>
<br>

macOS-use enables AI agents to interact with your Macbook [see examples below!](#examples)

# Quick start

⚠️ Important: Review the [Warning](#warning) section before proceeding. <br>

### Installation from GitHub

Clone first
<br>

```bash
git clone https://github.com/MihiroH/macOS-use-custom.git && cd macOS-use-custom
```

## LLM Provider Options

macOS-use supports multiple LLM providers:

### Option 1: Claude Code CLI (Recommended - Subscription-based)
Use Claude Code CLI to avoid pay-per-use API costs:
- Install [Claude Code CLI](https://claude.ai/cli) globally
- No API keys needed - uses your Claude subscription
- Set `LLM_PROVIDER=claude-cli` in your `.env` file

### Option 2: API-based Providers (Pay-per-use)
Supported providers: [OAI](https://platform.openai.com/docs/quickstart), [Anthropic](https://docs.anthropic.com/en/api/admin-api/apikeys/get-api-key) or [Gemini](https://ai.google.dev/gemini-api/docs/api-key) (deepseek R1 coming soon!)

<br> At the moment, macOS-use works best with OAI or Anthropic API, although Gemini is free. While Gemini works great too, it is not as reliable.
<br>

```bash
cp .env.example .env
```

```bash
open ./.env
```

### Configuration

Edit your `.env` file:

**For Claude CLI (Recommended):**
```bash
LLM_PROVIDER=claude-cli
```

**For API-based providers:**
```bash
LLM_PROVIDER=oai  # or anthropic, google
OPENAI_API_KEY=your_key_here
# or ANTHROPIC_API_KEY=your_key_here
# or GEMINI_API_KEY=your_key_here
```

We recommend using macOS-use with uv environment
<br>

```bash
brew install uv && uv venv && source .venv/bin/activate
```

Install locally and you're good to go! Try the first example!
<br>

```bash
uv pip install --editable . && python examples/try.py

```

Try prompting it with

```bash
open the calculator app
```

# Examples

Try these examples to see macOS-use in action:

## Calculator Example
Calculate mathematical expressions using the calculator app:

```bash
python examples/calculate.py
```

Example prompt: "Calculate how much is 5 X 4 and return the result, then call done."

## Authentication Example
Automate login processes:

```bash
python examples/login_to_auth0.py
```

## Time Check Example
Check time information online:

```bash
python examples/check_time_online.py
```

Example prompt: "Can you check what hour is Shabbat in israel today? call done when you finish."

## Claude CLI Test
Test the enhanced Claude CLI integration:

```bash
python examples/test_claude_cli.py
```

<br>

# Our Vision:

TLDR: Tell every Apple device what to do, and see it done. on EVERY APP.
<br><br>
This project aimes to build the AI agent for the MLX by Apple framework that would allow the agent to perform any action on any Apple device. Our final goal is a open source that anyone can clone, powered by the [mlx](https://github.com/ml-explore/mlx) and [mlx-vlm](https://github.com/Blaizzy/mlx-vlm) to run local private infrence at zero cost.

## Roadmap goals:

1. Support MacBooks at SOTA reliability

- [ ] Refine the Agent prompting.
- [ ] Release the first working version to pypi.
- [ ] Improve self-correction.
- [x] Adding ability to check which apps the machine has installed.
- [x] Add feature to allow the agent to check existing apps if failing, e.g. calendar app actual name is iCal.
- [ ] Add action for the agent to ask input from the user.
- [ ] Test Test Test! and let us know what and how to improve!
- [ ] Make task cheaper and more efficient.

2. Support local inference with small fine tuned model.

- [ ] Add support for inference with local models using mlx and mlx-vlm.
- [ ] Fine tune a small model that every device can run inference with.
- [ ] SOTA reliability.

3. Support iPhone/iPad

<br>

# WARNING

This project is still under development and user discretion is advised!
macOS-use can and will use your login credentials, private information, auth services, or stored passwords to complete its task, launch and interact WITH EVERY APP and UI component in your MacBook. Restrictions to the model are still under active development! It is not recommended to operate it unsupervised YET.
macOS-use WILL NOT STOP at captcha or any other forms of bot identifications, so once again, user discretion is advised.

## Disclaimer:

As this is an early stage release, you might experience varying success rates depending on task prompt. This is a customized version with additional features and improvements. For issues specific to this fork, please open an issue in this repository.

# Contributing

This is a customized fork with enhanced features. Contributions are welcome! Feel free to:

- Open issues for bugs or feature requests
- Submit pull requests for improvements
- Share feedback on the Claude CLI integration

For issues related to the core macOS-use functionality, please also consider contributing to the [original repository](https://github.com/browser-use/macOS-use).

# Acknowledgments

This project builds upon the excellent work of the original [browser-use/macOS-use](https://github.com/browser-use/macOS-use) team. Special thanks to:

- **Ofir Ozeri** - Original creator and vision
- **Gregor Zunic** - Core development and Browser Use foundation
- **Magnus** - Migration and development support

Their innovative work made this enhanced version possible.

# License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


