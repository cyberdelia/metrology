.. _ref-instruments:

===========
Instruments
===========

Counters
========

::

  counter = Metrology.counter('call')
  counter.increment()

Meters
======

::

  meter = Metrology.meter('request')
  meter.mark()


Timers
======

::

  timer = Metrology.timer('request')
  with timer:
      do_something()


Utilization Timers
==================

::

  utimer = Metrology.utilization_timer('request')
  with utimer:
      do_something()

