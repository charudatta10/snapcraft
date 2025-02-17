Remote build
============

Remote build is a feature in Snapcraft that offloads the build process to
`Launchpad`_'s `build farm`_ and enables developers to build snaps for
different architectures.

Architectures supported by Launchpad can be found
:ref:`here<supported-architectures>`.

Open vs closed source
---------------------

By default, prospective snaps must be open source because the build will be
publicly available.

Developers are reminded of this by confirming that their project will be
publicly available when starting a remote build. This prompt can be
automatically agreed to by passing ``--launchpad-accept-public-upload``.

Closed-source projects can be built using the remote builder. This requires
the user to create a private Launchpad project and pass the project with the
``--project <project-name>`` command line argument.

Git repository
--------------

Projects must be in the top level of a git repository because snapcraft uses
a git-based workflow to upload projects to Launchpad.

Shallowly cloned repositories are not supported (e.g. ``git clone --depth
1``)
because git does not support pushing shallow clones.

Versions
--------

Two versions of the remote-builder are available, the current and the legacy
remote-builder.

Current
^^^^^^^

The current remote builder is available for ``core22``, ``core24``,
and newer snaps.  It is not available for ``core20`` snaps because it cannot
parse ``core20``'s ``snapcraft.yaml`` schema (`[10]`_).

It does not modify the project or project metadata.

Legacy
^^^^^^

The "fallback" or legacy version of the remote builder can be used for
``core20`` and ``core22`` snaps.  It is not available for ``core24`` and newer
snaps.

The legacy remote builder was deprecated because of its design. It retrieves
and tarballs remote sources and modifies the project's ``snapcraft.yaml``
file to point to the local tarballs. This caused many unexpected failures that
could not be reproduced locally.

Choosing a remote-builder
^^^^^^^^^^^^^^^^^^^^^^^^^

The environment variable ``SNAPCRAFT_REMOTE_BUILD_STRATEGY`` determines which
remote-builder is used:

* ``disable-fallback`` will use the current remote builder
* ``force-fallback`` will use the legacy remote builder

If the environment variable is unset, the remote builder will be determined
by the base:

* ``core22``, ``core24``, and newer snaps will use the current remote builder
* ``core20`` snaps will use the legacy remote builder

Platforms and architectures
---------------------------

Remote builds can be orchestrated for multiple platforms and architectures.

Current
^^^^^^^

``--build-for``
***************

.. note::
   ``--build-for`` behaves differently for ``remote-build`` than it does for
   :ref:`lifecycle commands<reference-lifecycle-commands>`.

Remote builds are useful for building snaps on different architectures. Due
to this, the semantics for the ``--build-for`` argument is more complex than
when building a snap locally.

The argument operates in one of two different ways depending on the presence
of a ``platforms`` or ``architectures`` key in the project file.

The first mode of operation is when the ``platforms`` or ``architectures``
key is present in the project file. In this scenario, ``--build-for`` operates
similar to how it does for lifecycle commands. The difference from its usage in
lifecycle commands is that ``--build-for`` may be a comma-separated list, which
allows multiple snaps to be built. For more information about build plans and
filtering, see :ref:`Build plans <build-plans>`.

The second mode of operation is when there isn't a ``platforms`` or
``architectures`` key in the project file. In this scenario, ``--build-for``
defines the architectures to build for.

Project platforms and architectures
***********************************

The ``snapcraft.yaml`` file is always parsed by the new remote builder.

If the project metadata contains a ``platforms`` or ``architectures`` entry,
Snapcraft will request a build for each unique ``build-for`` architecture.

.. note::

   Launchpad does not support cross-compiling (`[13]`_).

.. note::

    Launchpad does not support building multiple snaps on the same
    ``build-on`` architecture (`[14]`_).

If the project metadata does not contain a ``platforms`` or ``architectures``
entry and ``--build-for`` is not provided, Snapcraft will request a build on,
and for, the host's architecture.

The remote builder does not work for ``core20`` snaps because it cannot parse
the ``run-on`` keyword in a ``core20`` architecture entry (`[2]`_).

Legacy
^^^^^^

``--build-for`` and ``--build-on``
**********************************

The Launchpad build farm was designed for native builds and does not
have a concept of a ``build-for`` architecture.

The legacy remote builder accepts ``--build-on`` and ``--build-for``.
Since developers are typically interested in the ``build-for`` of
a snap, snapcraft converts the ``--build-for`` to ``--build-on``.

These parameters are not mutually exclusive and ``--build-for`` takes
precedence over ``--build-on``.

Both of these parameters accept a comma-separated list of architectures.
Snapcraft will request builds to occur on each specified architecture.

Project architectures
*********************

If the ``snapcraft.yaml`` file contains the top-level ``architectures``
keyword, snapcraft will request a build for each ``build-on`` architecture.

An architecture can only be listed once across all ``build-on`` keys in the
``architectures`` keyword, otherwise Snapcraft will fail to parse the
project (`[4]`_).

If no architectures are defined in the project metadata, snapcraft will
request a build for the host's architecture.

``--build-for`` and ``--build-on`` cannot be provided when the
``architectures`` keyword is defined in the project metadata. This is because
Launchpad will ignore the requested architectures and prefer those defined
in the ``snapcraft.yaml`` (`[5]`_).

The legacy remote builder can be used for ``core20`` and ``core22`` snaps but
the project is parsed using ``core20``'s ``snapcraft.yaml`` schema. This
means that snaps using keywords introduced in ``core22`` cannot be built with
the remote builder (`[6]`_ `[7]`_ `[8]`_). This includes the ``core22``
``architectures`` keyword change of ``run-on`` to ``build-for``.

Similarly, ``core22`` supports a shorthand notation for ``architectures`` but
Launchpad is not able to parse this notation (`[9]`_).

.. _`Launchpad account`: https://launchpad.net/+login
.. _`Launchpad`: https://launchpad.net/
.. _`build farm`: https://launchpad.net/builders
.. _`[2]`: https://github.com/canonical/snapcraft/issues/4842
.. _`[4]`: https://github.com/canonical/snapcraft/issues/4341
.. _`[5]`: https://bugs.launchpad.net/snapcraft/+bug/1885150
.. _`[6]`: https://github.com/canonical/snapcraft/issues/4144
.. _`[7]`: https://bugs.launchpad.net/snapcraft/+bug/1992557
.. _`[8]`: https://bugs.launchpad.net/snapcraft/+bug/2007789
.. _`[9]`: https://bugs.launchpad.net/snapcraft/+bug/2042167
.. _`[10]`: https://github.com/canonical/snapcraft/issues/4885
.. _`[13]`: https://github.com/canonical/snapcraft/issues/4996
.. _`[14]`: https://github.com/canonical/snapcraft/issues/4995
