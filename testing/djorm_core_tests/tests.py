# -*- coding: utf-8 -*-

from django.test import TestCase

from djorm_core.postgresql import server_side_cursors
from .models import TestModel


class ServerSideCursorsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        TestModel.objects.bulk_create([TestModel(num=x) for x in range(200)])

    @classmethod
    def tearDownClass(cls):
        TestModel.objects.all().delete()

    def test_simple_01(self):
        with self.assertNumQueries(1):
            self.assertEqual(len([x for x in TestModel.objects.all()]), 200)

    def test_simple_02(self):
        with self.assertNumQueries(1):
            with server_side_cursors():
                self.assertEqual(len([x for x in TestModel.objects.all()]), 200)
