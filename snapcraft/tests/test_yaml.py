# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright (C) 2015 Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import jsonschema
import logging
import os
import tempfile
import unittest

import fixtures

from snapcraft import dirs
from snapcraft.yaml import (
    _validate_snapcraft_yaml,
    Config,
)
from snapcraft.tests import TestCase


class TestYaml(TestCase):

    def make_snapcraft_yaml(self, content):
        tempdirObj = tempfile.TemporaryDirectory()
        self.addCleanup(tempdirObj.cleanup)
        os.chdir(tempdirObj.name)
        with open("snapcraft.yaml", "w") as fp:
            fp.write(content)

    @unittest.mock.patch('snapcraft.yaml.Config.load_plugin')
    def test_config_loads_plugins(self, mock_loadPlugin):
        dirs.setup_dirs()

        self.make_snapcraft_yaml("""name: test
version: "1"
vendor: me <me@me.com>
summary: test
description: test

parts:
  ubuntu:
    packages: [fswebcam]
""")
        Config()
        mock_loadPlugin.assert_called_with("ubuntu", "ubuntu", {
            "packages": ["fswebcam"],
        })

    def test_config_raises_on_missing_snapcraft_yaml(self):
        fake_logger = fixtures.FakeLogger(level=logging.ERROR)
        self.useFixture(fake_logger)

        # no snapcraft.yaml
        with self.assertRaises(SystemExit) as raised:
            Config()

        self.assertEqual(raised.exception.code, 1, 'Wrong exit code returned.')
        self.assertEqual(
            "Could not find snapcraft.yaml.  Are you sure you're in the right directory?\n"
            "To start a new project, use 'snapcraft init'\n",
            fake_logger.output)

    def test_config_loop(self):
        dirs.setup_dirs()

        fake_logger = fixtures.FakeLogger(level=logging.ERROR)
        self.useFixture(fake_logger)

        self.make_snapcraft_yaml("""name: test
version: "1"
vendor: me <me@me.com>
summary: test
description: test

parts:
  p1:
    plugin: ubuntu
    after: [p2]
  p2:
    plugin: ubuntu
    after: [p1]
""")
        with self.assertRaises(SystemExit) as raised:
            Config()

        self.assertEqual(raised.exception.code, 1, 'Wrong exit code returned.')
        self.assertEqual('Circular dependency chain!\n', fake_logger.output)

    @unittest.mock.patch('snapcraft.yaml.Config.load_plugin')
    def test_invalid_yaml_missing_name(self, mock_loadPlugin):
        dirs.setup_dirs()

        fake_logger = fixtures.FakeLogger(level=logging.ERROR)
        self.useFixture(fake_logger)

        self.make_snapcraft_yaml("""
version: "1"
vendor: me <me@me.com>
summary: test
description: nothing

parts:
  ubuntu:
    packages: [fswebcam]
""")
        with self.assertRaises(SystemExit) as raised:
            Config()

        self.assertEqual(raised.exception.code, 1, 'Wrong exit code returned.')
        self.assertEqual(
            'Issues while validating snapcraft.yaml: \'name\' is a required property\n',
            fake_logger.output)

    @unittest.mock.patch('snapcraft.yaml.Config.load_plugin')
    def test_invalid_yaml_invalid_name_as_number(self, mock_loadPlugin):
        dirs.setup_dirs()

        fake_logger = fixtures.FakeLogger(level=logging.ERROR)
        self.useFixture(fake_logger)

        self.make_snapcraft_yaml("""name: 1
version: "1"
vendor: me <me@me.com>
summary: test
description: nothing

parts:
  ubuntu:
    packages: [fswebcam]
""")
        with self.assertRaises(SystemExit) as raised:
            Config()

        self.assertEqual(raised.exception.code, 1, 'Wrong exit code returned.')
        self.assertEqual(
            'Issues while validating snapcraft.yaml: 1 is not of type \'string\'\n',
            fake_logger.output)

    @unittest.mock.patch('snapcraft.yaml.Config.load_plugin')
    def test_invalid_yaml_invalid_name_chars(self, mock_loadPlugin):
        dirs.setup_dirs()

        fake_logger = fixtures.FakeLogger(level=logging.ERROR)
        self.useFixture(fake_logger)

        self.make_snapcraft_yaml("""name: myapp@me_1.0
version: "1"
vendor: me <me@me.com>
summary: test
description: nothing

parts:
  ubuntu:
    packages: [fswebcam]
""")
        with self.assertRaises(SystemExit) as raised:
            Config()

        self.assertEqual(raised.exception.code, 1, 'Wrong exit code returned.')
        self.assertEqual(
            'Issues while validating snapcraft.yaml: \'myapp@me_1.0\' does not match \'^[a-z0-9][a-z0-9+-]*$\'\n',
            fake_logger.output)

    @unittest.mock.patch('snapcraft.yaml.Config.load_plugin')
    def test_invalid_yaml_missing_description(self, mock_loadPlugin):
        dirs.setup_dirs()

        fake_logger = fixtures.FakeLogger(level=logging.ERROR)
        self.useFixture(fake_logger)

        self.make_snapcraft_yaml("""name: test
version: "1"
vendor: me <me@me.com>
summary: test

parts:
  ubuntu:
    packages: [fswebcam]
""")
        with self.assertRaises(SystemExit) as raised:
            Config()

        self.assertEqual(raised.exception.code, 1, 'Wrong exit code returned.')
        self.assertEqual(
            'Issues while validating snapcraft.yaml: \'description\' is a required property\n',
            fake_logger.output)


class TestValidation(TestCase):

    def setUp(self):
        super().setUp()
        dirs.setup_dirs()

        self.data = {
            'name': 'my-package-1',
            'version': '1.0-snapcraft1~ppa1',
            'vendor': 'Me <me@me.com>',
            'summary': 'my summary less that 79 chars',
            'description': 'description which can be pretty long',
            'parts': {
                'part1': {
                    'type': 'project',
                },
            },
        }

    def test_required_properties(self):
        for key in self.data:
            data = self.data.copy()
            with self.subTest(key=key):
                del data[key]

                with self.assertRaises(jsonschema.ValidationError) as raised:
                    _validate_snapcraft_yaml(data)

                expected_message = '\'{}\' is a required property'.format(key)
                self.assertEqual(raised.exception.message, expected_message, msg=data)

    def test_invalid_names(self):
        invalid_names = [
            'package@awesome',
            'something.another',
            '_hideme',
        ]

        for name in invalid_names:
            data = self.data.copy()
            with self.subTest(key=name):
                data['name'] = name

                with self.assertRaises(jsonschema.ValidationError) as raised:
                    _validate_snapcraft_yaml(data)

                expected_message = '\'{}\' does not match \'^[a-z0-9][a-z0-9+-]*$\''.format(name)
                self.assertEqual(raised.exception.message, expected_message, msg=data)

    def test_summary_too_long(self):
        self.data['summary'] = 'a' * 80
        with self.assertRaises(jsonschema.ValidationError) as raised:
            _validate_snapcraft_yaml(self.data)

        expected_message = '\'{}\' is too long'.format(self.data['summary'])
        self.assertEqual(raised.exception.message, expected_message, msg=self.data)

    def test_valid_types(self):
        self.data['type'] = 'app'
        _validate_snapcraft_yaml(self.data)

        self.data['type'] = 'framework'
        _validate_snapcraft_yaml(self.data)

    def test_invalid_types(self):
        invalid_types = [
            'apps',
            'kernel',
            'platform',
            'oem',
            'os',
        ]

        for t in invalid_types:
            data = self.data.copy()
            with self.subTest(key=t):
                data['type'] = t

                with self.assertRaises(jsonschema.ValidationError) as raised:
                    _validate_snapcraft_yaml(data)

                expected_message = '\'{}\' is not one of [\'app\', \'framework\']'.format(t)
                self.assertEqual(raised.exception.message, expected_message, msg=data)

    def test_valid_services(self):
        self.data['services'] = [
            {
                'name': 'service1',
                'start': 'binary1 start',
            },
            {
                'name': 'service2',
                'start': 'binary2',
                'stop': 'binary2 --stop',
            },
            {
                'name': 'service3',
            }
        ]

        _validate_snapcraft_yaml(self.data)

    def test_services_required_properties(self):
        self.data['services'] = [
            {
                'start': 'binary1 start',
            }
        ]

        with self.assertRaises(jsonschema.ValidationError) as raised:
            _validate_snapcraft_yaml(self.data)

        expected_message = '\'name\' is a required property'
        self.assertEqual(raised.exception.message, expected_message, msg=self.data)
