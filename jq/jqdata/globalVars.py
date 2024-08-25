import six
import pickle
class GlobalVars(object):
    def get_state(self):
        dict_data = {}
        for key, value in six.iteritems(self.__dict__):
            try:
                dict_data[key] = pickle.dumps(value)
            except Exception as e:
                print('CCC')
        return pickle.dumps(dict_data)

    def set_state(self, state):
        dict_data = pickle.loads(state)
        for key, value in six.iteritems(dict_data):
            try:
                self.__dict__[key] = pickle.loads(value)
            except Exception as e:
                print('CCC')
