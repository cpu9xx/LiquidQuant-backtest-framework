from .events import EVENT, Event

class Executor(object):
    def __init__(self, env):
        self._env = env

    KNOWN_EVENTS = {
        EVENT.TICK,
        EVENT.BAR,
        EVENT.BEFORE_TRADING,
        EVENT.AFTER_TRADING,
        EVENT.POST_SETTLEMENT,
    }

    def run(self, bar_dict):

        start = self._env.usercfg['start']
        end = self._env.usercfg['end']
        frequency = self._env.config.base.frequency
        event_bus = self._env.event_bus

        for event in self._env.event_source.events(start, end, frequency):
            if event.event_type in self.KNOWN_EVENTS:
                self._env.calendar_dt = event.calendar_dt
                #self._env.trading_dt = event.trading_dt

                event_bus.publish_event(event)
