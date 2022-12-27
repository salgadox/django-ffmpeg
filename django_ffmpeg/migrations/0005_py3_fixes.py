# Generated by Django 2.2.5 on 2019-09-20 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("django_ffmpeg", "0004_video_title_not_required"),
    ]

    operations = [
        migrations.AlterField(
            model_name="convertingcommand",
            name="command",
            field=models.TextField(
                help_text="Example: /usr/bin/ffmpeg -nostats -y -i %(input_file)s -acodec libmp3lame -ar 44100 -f flv %(output_file)s",
                verbose_name="System command to convert video",
            ),
        ),
        migrations.AlterField(
            model_name="convertingcommand",
            name="match_by",
            field=models.CharField(
                choices=[("extension", "Extension"), ("name", "File name")],
                default="extension",
                help_text="Video param to detected from if this command should be used to convert given video",
                max_length=50,
                verbose_name="Match by",
            ),
        ),
        migrations.AlterField(
            model_name="convertingcommand",
            name="thumb_command",
            field=models.TextField(
                help_text="Example: /usr/bin/ffmpeg -hide_banner -nostats -i %(in_file)s -y -frames:v 1 -ss %(thumb_frame)s %(out_file)s",
                verbose_name="System command to convert thumb",
            ),
        ),
        migrations.AlterField(
            model_name="video",
            name="convert_status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending convert"),
                    ("started", "Convert started"),
                    ("converted", "Converted"),
                    ("error", "Not converted due to error"),
                ],
                default="pending",
                max_length=16,
                verbose_name="Video conversion status",
            ),
        ),
    ]
