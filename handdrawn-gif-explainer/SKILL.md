---
name: handdrawn-gif-explainer
description: Create looping hand-drawn-style GIF explainers from a concept, process, or architecture. Use when the user wants sketchbook animation, animated handwritten diagrams, or a visually simple step-by-step GIF.
---

# Hand-drawn GIF explainer

Every invocation must create an original visual concept, art direction, composition, and animation specifically for the subject. For a batch, make each deliverable visibly distinct in style and design. Do not use generic AI slop: repeated boxes and arrows, canned corporate infographic layouts, a stock paper background with the same shapes, or simple color swaps. Never ship the bundled renderer's default grid, parallel, or flow layouts as finished work. The renderer is a technical reference only; create bespoke artwork and animation. Show meaningful progression, not a static diagram with a moving highlight.

Prefer an available drawing or image-generation tool to create the artwork for the GIF. Use its images as artwork or animation source frames, then animate and encode them into a GIF with suitable tools. If no suitable drawing tool is available, create the artwork with other available techniques. Check the result visually and correct unreadable generated text with a reliable typesetting method when needed.

For every invocation, generate a fresh cryptographically secure random string before developing the visual concept; for a batch, generate a separate string for each deliverable. For example, run `python -c 'import secrets; print(secrets.token_hex(16))'`. Draw creative inspiration from the string's characters, patterns, or associations and translate it into concrete choices such as visual metaphor, composition, materials, color, or motion. Do not merely display the string or make a superficial color swap. The random seed is inspiration, not an override of the user's requirements, the subject's accuracy, or legibility. Do not use ordinary pseudorandom generators or reuse a previous seed.

For command-line workflows, consider a deliberately designed terminal session: animated typing, truthful example output, errors or verification where relevant, and a clear iterative loop. Distinguish illustrative output from an actual captured session.

Turn the subject into a short visual story with a few distinct, readable scenes. Favor paper texture, loose ink lines, handwritten typography, restrained colors and purposeful motion. Avoid glossy corporate cards, generic AI infographics and purely decorative movement unless the user asks for them.

1. Identify the audience, central idea, language and output context. Verify technical claims and make clear when a scene illustrates a proposed or incomplete design.
2. Storyboard the minimum scenes needed: each should communicate one point on its own and stay visible long enough to read. Prefer visual changes that explain the process over repeated pulsing or movement for its own sake.
3. Create a bespoke visual design and animation for this invocation. The bundled Pillow renderer may be inspected for technical ideas, but its template layouts are not acceptable as finished work. Use an appropriate handwriting font that covers the requested language; supply its path explicitly when needed. Do not redistribute fonts without checking their license.
4. Render a GIF that loops cleanly, then inspect representative frames from every scene at actual display size and check the animation, total duration, text clipping, contrast and file size. Correct the result rather than relying on successful encoding. Preserve truthful labels and distinguish illustrations from actual screenshots.
5. Provide the resulting file. If the user authorizes publishing it, verify the hosted URL serves the GIF and confirm the destination actually displays it. Do not assume that saving locally or hosting an image updates the requested page.

Do not overwrite existing user files without authorization. Use a scratch directory for temporary frames and leave only requested deliverables.
