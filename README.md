# Metrology

A library to easily measure what's going on in your python.

### Installing

To install :

    pip install metrology

## API

### Counters

    >>> from metrology import Metrology
    >>> counter = Metrology.counter('call')
    >>> counter.increment()

### Meters

    >>> from metrology import Metrology
    >>> meter = Metrology.meter('request')
    >>> meter.mark()

### Timers

    >>> from metrology import Metrology
    >>> timer = Metrology.timer('request')
    >>> with timer:
    ...     do()

### Utilization Timer

    >>> from metrology import Metrology
    >>> meter = Metrology.utilization_timer('request')    

## Reporters

### Logger Reporter

    >>> from metrology.reporter.logger import LoggerReporter
    >>> reporter = LoggerReporter()
    >>> reporter.start()

### Graphite Reporter

    >>> from metrology.reporter.graphite import GraphiteReporter
    >>> reporter = GraphiteReporter('localhost', 3333)
    >>> reporter.start()


### Acknowledgement

This is heavily inspired by the awesome [metrics](https://github.com/codahale/metrics) library.
