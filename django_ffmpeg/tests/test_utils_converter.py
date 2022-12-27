import logging
import time

from django.conf import settings
from django.test import tag

from django_ffmpeg.models import VIDEO_CONVERSION_STATUS_CHOICES as STATUS
from django_ffmpeg.tests.base import BaseTestCase
from django_ffmpeg.utils import Converter

logger = logging.getLogger(__name__)


CONV_TIMEOUT = getattr(settings, "FFMPEG_TEST_CONV_TIMEOUT", 30)
EMULATION = getattr(settings, "FFMPEG_TEST_EMULATION", True)


class PendingConvertTest(BaseTestCase):
    @tag("ffmpeg-converter")
    def test_success_convert_pending(self):
        user = self.create_superuser()
        self.create_command()
        video = self.create_video_file(user)
        self.assertEqual(video.convert_status, STATUS[0][0])
        converter = Converter()
        converter.emulation = EMULATION
        converter.convert_first_pending()
        time.sleep(CONV_TIMEOUT)
        video.refresh_from_db()
        self.assertEqual(video.convert_status, STATUS[2][0])
        self.remove_video_file(video)
