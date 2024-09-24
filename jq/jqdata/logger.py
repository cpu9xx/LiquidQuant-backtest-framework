from .Env import Env
class Log:
    def __init__(self):
        try:
            self._env = Env.get_instance()
        except:
            self._env = None

    def set_env(self, environment):
        self._env = environment

    def info(self, message):
        print(f"--{self._env.current_dt} : {message}")

    def error(self, message):
        print(f"--{self._env.current_dt} : {message}")
        raise Exception(message)
    
    def warning(self, message):
        print(f"\033[31m--{self._env.current_dt} : {message}\033[0m")

    def test(self, *messages):
        combined_message = ' '.join(map(str, messages))
        print(f"\033[34m--{self._env.current_dt} : {combined_message}\033[0m")

log = Log()