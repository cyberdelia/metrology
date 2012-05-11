

class HealthCheck(object):
    """
    A health check is a small self-test to verify that a specific component or responsibility is performing correctly ::

      class DatabaseHealthCheck(metrology.healthcheck.HealthCheck):
          def __init__(self, database):
              self.database = database

          def check(self):
              if database.ping():
                  return True
              return False

      health_check = Metrology.health_check('database', DatabaseHealthCheck(database))
      health_check.check()

    """
    def check(self):
        """Returns True if what is being checked is healthy"""
        raise NotImplementedError
