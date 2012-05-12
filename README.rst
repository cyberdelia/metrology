=========
Metrology
=========

A library to easily measure what's going on in your python.

Metrology allows you to add instruments to your python code and hook them to external reporting tools like Graphite so as to better understand what's going on in your running python program.

Installing
==========

To install : ::

    pip install metrology

API
===

Gauge
-----

A gauge is an instantaneous measurement of a value ::

    class JobGauge(metrology.instruments.Gauge):
        def value(self):
            return len(queue)
    gauge = Metrology.gauge('pending-jobs', JobGauge())


Counters
--------

A counter is like a gauge, but you can increment or decrement its value ::

    counter = Metrology.counter('pending-jobs')
    counter.increment()
    counter.decrement()
    counter.count

Meters
------

A meter measures the rate of events over time (e.g., "requests per second").
In addition to the mean rate, you can also track 1, 5 and 15 minutes moving averages ::

    meter = Metrology.meter('requests')
    meter.mark()
    meter.count

Timers
------

A timer measures both the rate that a particular piece of code is called and the distribution of its duration ::

    timer = Metrology.timer('responses')
    with timer:
        do_something()


Utilization Timer
-----------------

A specialized timer that calculates the percentage of wall-clock time that was spent ::
    
    utimer = Metrology.utilization_timer('responses')
    with utimer:
      do_something()


Reporters
=========

Logger Reporter
---------------

A logging reporter that write metrics to a logger ::

    reporter = LoggerReporter(level=logging.INFO, interval=10)
    reporter.start()


Graphite Reporter
-----------------

A graphite reporter that send metrics to graphite ::
    
    reporter = GraphiteReporter('graphite.local', 2003)
    reporter.start()


Acknowledgement
===============

This is heavily inspired by the awesome `metrics <https://github.com/codahale/metrics>`_ library.
