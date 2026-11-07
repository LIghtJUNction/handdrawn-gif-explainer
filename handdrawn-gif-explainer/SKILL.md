---
name: handdrawn-gif-explainer
description: Create looping hand-drawn-style GIF explainers from a concept, process, or architecture. Use when the user wants sketchbook animation, animated handwritten diagrams, or a visually simple step-by-step GIF.
---

# Hand-drawn GIF explainer

Turn the subject into a short visual story with a few distinct, readable scenes. Favor paper texture, loose ink lines, handwritten typography, restrained colors and purposeful motion. Avoid glossy corporate cards, generic AI infographics and purely decorative movement unless the user asks for them.

1. Identify the audience, central idea, language and output context. Verify technical claims and make clear when a scene illustrates a proposed or incomplete design.
2. Storyboard the minimum scenes needed: each should communicate one point on its own and stay visible long enough to read. Prefer visual changes that explain the process over repeated pulsing or movement for its own sake.
3. Use `scripts/render.py --help` for the bundled Pillow renderer's input format and options. It provides a starting point, not a fixed template: adapt its drawing code or create a different animation when the story calls for it. Use an appropriate handwriting font that covers the requested language; supply its path explicitly when needed. Do not redistribute fonts without checking their license.
4. Render a GIF that loops cleanly, then inspect representative frames from every scene at actual display size and check the animation, total duration, text clipping, contrast and file size. Correct the result rather than relying on successful encoding. Preserve truthful labels and distinguish illustrations from actual screenshots.
5. Provide the resulting file. If the user authorizes publishing it, verify the hosted URL serves the GIF and confirm the destination actually displays it. Do not assume that saving locally or hosting an image updates the requested page.

Do not overwrite existing user files without authorization. Use a scratch directory for temporary frames and leave only requested deliverables.
