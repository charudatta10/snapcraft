# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2023 Canonical Ltd.
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

"""Snapcraft services."""

from snapcraft.services.assertions import AssertionService
from snapcraft.services.lifecycle import Lifecycle
from snapcraft.services.package import Package
from snapcraft.services.provider import Provider
from snapcraft.services.registries import RegistriesService
from snapcraft.services.remotebuild import RemoteBuild
from snapcraft.services.service_factory import SnapcraftServiceFactory

__all__ = [
    "AssertionService",
    "Lifecycle",
    "Package",
    "Provider",
    "RegistriesService",
    "RemoteBuild",
    "SnapcraftServiceFactory",
]
