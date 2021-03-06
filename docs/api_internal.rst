======================
API - Internal Devices
======================

.. module:: gpiozero.internal_devices

.. currentmodule:: gpiozero

GPIO Zero also provides several "internal" devices which represent facilities
provided by the operating system itself. These can be used to react to things
like the time of day, or whether a server is available on the network.

.. warning::

    These devices are experimental and their API is not yet considered stable.
    We welcome any comments from testers, especially regarding new "internal
    devices" that you'd find useful!


TimeOfDay
=========

.. autoclass:: TimeOfDay
    :members: is_active

PingServer
==========

.. autoclass:: PingServer
    :members: is_active

CPUTemperature
==============

.. autoclass:: CPUTemperature
    :members: temperature, is_active

LoadAverage
===========

.. autoclass:: LoadAverage
    :members: load_average, is_active

Base Classes
============

The classes in the sections above are derived from a series of base classes,
some of which are effectively abstract. The classes form the (partial)
hierarchy displayed in the graph below (abstract classes are shaded lighter
than concrete classes):

.. image:: images/other_device_hierarchy.*

The following sections document these base classes for advanced users that wish
to construct classes for their own devices.

InternalDevice
==============

.. autoclass:: InternalDevice()
