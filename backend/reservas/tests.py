from datetime import date, datetime, timezone as datetime_timezone

from django.test import SimpleTestCase, override_settings
from django.utils.dateparse import parse_datetime
from rest_framework import serializers


class DateSerializationTests(SimpleTestCase):
    def test_date_field_preserves_calendar_date(self):
        field = serializers.DateField()

        self.assertEqual(field.to_representation(date(2026, 6, 21)), '2026-06-21')

    @override_settings(TIME_ZONE='America/Lima', USE_TZ=True)
    def test_datetime_field_preserves_instant_and_uses_lima_offset(self):
        field = serializers.DateTimeField()
        instant = datetime(2026, 6, 22, 2, 15, 30, tzinfo=datetime_timezone.utc)

        serialized = field.to_representation(instant)

        self.assertEqual(serialized, '2026-06-21T21:15:30-05:00')
        self.assertEqual(parse_datetime(serialized).astimezone(datetime_timezone.utc), instant)
