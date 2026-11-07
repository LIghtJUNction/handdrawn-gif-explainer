import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

SCRIPT = Path(__file__).resolve().parents[1] / "handdrawn-gif-explainer/scripts/render.py"


class RendererTests(unittest.TestCase):
    def run_renderer(self, payload, directory, output="out.gif"):
        source = directory / "story.json"
        source.write_text(json.dumps(payload), encoding="utf-8")
        return subprocess.run([sys.executable, str(SCRIPT), str(source), str(directory / output)], capture_output=True, text=True)

    def test_multiple_scenes_form_one_timed_loop_and_preserve_existing_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            payload = {"width": 320, "height": 240, "frames": 4, "duration": 100,
                       "scenes": [{"scene": "grid", "labels": ["one"]},
                                  {"scene": "flow", "labels": ["in", "out"]}]}
            result = self.run_renderer(payload, directory)
            self.assertEqual(result.returncode, 0, result.stderr)
            output = directory / "out.gif"
            before = output.read_bytes()
            with Image.open(output) as image:
                self.assertEqual(image.info.get("loop"), 0)
                self.assertEqual(image.size, (320, 240))
                duration = 0
                for i in range(image.n_frames):
                    image.seek(i)
                    duration += image.info["duration"]
                self.assertEqual(duration, 800)
            result = self.run_renderer(payload, directory)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(output.read_bytes(), before)

    def test_invalid_or_oversized_input_does_not_create_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            result = self.run_renderer({"scenes": [{"scene": "unknown"}]}, directory)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((directory / "out.gif").exists())
            result = self.run_renderer({"scene": "grid", "width": 1920, "height": 1080, "frames": 120}, directory)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((directory / "out.gif").exists())


if __name__ == "__main__":
    unittest.main()
