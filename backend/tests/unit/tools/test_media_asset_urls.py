import os
import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.tools.media_assets import MediaAssetURLBuilder


class MediaAssetURLBuilderTests(unittest.TestCase):
    def test_default_base_url_points_to_local_audio_mount(self) -> None:
        builder = MediaAssetURLBuilder(base_url="/audio")
        self.assertEqual(
            builder.build("meditation/calm-reset.m4a"),
            "/audio/meditation/calm-reset.m4a",
        )

    def test_https_base_url_supports_cdn_hosting(self) -> None:
        builder = MediaAssetURLBuilder(base_url="https://cdn.example.com/mimind-assets/")
        self.assertEqual(
            builder.build("/meditation/calm-reset.m4a"),
            "https://cdn.example.com/mimind-assets/meditation/calm-reset.m4a",
        )

    def test_reads_base_url_from_environment_when_not_explicitly_provided(self) -> None:
        original = os.getenv("MEDIA_ASSET_BASE_URL")
        try:
            os.environ["MEDIA_ASSET_BASE_URL"] = "https://assets.mimind.example/static"
            builder = MediaAssetURLBuilder()
            self.assertEqual(
                builder.build("meditation/focus-grounding.m4a"),
                "https://assets.mimind.example/static/meditation/focus-grounding.m4a",
            )
        finally:
            if original is None:
                os.environ.pop("MEDIA_ASSET_BASE_URL", None)
            else:
                os.environ["MEDIA_ASSET_BASE_URL"] = original


if __name__ == "__main__":
    unittest.main()
