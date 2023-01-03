import datetime
import logging
import os
import re
import subprocess
import tempfile
from os import path

from pytz import timezone

from django_ffmpeg.models import ConvertingCommand, Video

logger = logging.getLogger(__name__)


class Converter(object):

    emulation = False

    def convert_first_pending(self):
        """"""
        video = self.choose_video()
        if not video:
            logger.info("No video found. Bypassing call...")
            return
        cmd = self.choose_convert_command(video)
        if not cmd:
            logger.error("Conversion command not found...")
            video.convert_status = "error"
            video.last_convert_msg = "Conversion command not found"
            video.save()
            return
        self.convert_video_thumb(cmd, video)
        self.convert_video_file(cmd, video)

    def call_cli(
        self, cmd, cmd_kwargs, storage=None, video_name=None, without_output=False
    ):
        """OS independency invoking of command line interface"""

        def _call_cli(command):
            logger.info("Calling command: %s" % command)
            if self.emulation:
                return logger.debug("Call: %s" % command)

            command_args = command.split()
            if without_output:
                DEVNULL = open(os.devnull, "wb")
                subprocess.run(command_args, stdout=DEVNULL, stderr=DEVNULL)
            else:
                result = subprocess.run(command_args, stdout=subprocess.PIPE)
                return result.stdout

        if storage is None:
            return _call_cli(cmd % cmd_kwargs)
        else:
            tmp_input_file = tempfile.NamedTemporaryFile()
            with storage.open(video_name, "rb") as src:
                tmp_input_file.write(src.read())
            tmp_output_file = tempfile.NamedTemporaryFile(
                suffix=path.splitext(cmd_kwargs["output_file"])[1]
            )

            _cmd_kwargs = cmd_kwargs.copy()
            _cmd_kwargs["input_file"] = tmp_input_file.name
            _cmd_kwargs["output_file"] = tmp_output_file.name
            out = _call_cli(cmd % _cmd_kwargs)

            # close the input temp file
            tmp_input_file.close()

            # reset the file pointer to the beginning of the file
            tmp_output_file.seek(0)

            # write the tmp file to the storage
            with storage.open(tmp_output_file, "wb") as dst:
                dst.write(tmp_output_file.read())

            # clouse the output temp file
            tmp_output_file.close()

            # return the stdout
            return out

    def choose_video(self):
        """First unconverted video"""
        return (
            Video.objects.filter(convert_status="pending")
            .order_by("created_at")
            .first()
        )

    def choose_convert_command(self, video):
        """Command for video converting by matching with video file name"""
        filepath = video.filepath
        filename = filepath.split("/")[-1]
        video_info = {
            "name": filename,
            "extension": filename.split(".")[-1],
        }
        cmds = ConvertingCommand.objects.filter(is_enabled=True)
        for c in cmds:
            match_by = video_info.get(c.match_by)
            if not match_by:
                continue
            if re.match(c.match_regex, match_by):
                return c

    def convert_video_file(self, cmd, video):
        """"""
        video.convert_status = "started"
        video.save()
        video.convert_extension = cmd.convert_extension
        try:
            if video.is_local:
                storage = None
            else:
                storage = video.video.storage

            cmd_kwargs = {
                "input_file": video.filepath,
                "output_file": video.converted_path,
            }
            # logger.info("Converting video command: %s" % c)
            output = self.call_cli(
                cmd.command, cmd_kwargs, storage=storage, video_name=video.video.name
            )
            logger.info("Converting video result: %s" % output)
        except Exception as e:
            logger.error("Converting video error", exc_info=True)
            video.convert_status = "error"
            video.last_convert_msg = "Exception while converting"
            video.save()
            return
        video.convert_status = (
            "error"
            if output and output.find("Conversion failed") != -1
            else "converted"
        )
        video.last_convert_msg = repr(output).replace("\\n", "\n").strip("'")
        video.converted_at = datetime.datetime.now(tz=timezone("UTC"))
        video.save()

    def convert_video_thumb(self, cmd, video):
        """"""
        try:
            if not video.thumb:
                if video.is_local:
                    storage = None
                else:
                    storage = video.video.storage

                cmd_kwargs = {
                    "input_file": video.filepath,
                    "output_file": video.thumb_video_path,
                    "thumb_frame": video.thumb_frame,
                }
                self.call_cli(
                    cmd.thumb_command,
                    cmd_kwargs,
                    storage=storage,
                    video_name=video.video.name,
                    without_output=True,
                )
            # logger.info("Creating thumbnail command: %s" % cmd)
        except:
            logger.error("Converting thumb error", exc_info=True)
