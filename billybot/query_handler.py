from collections import OrderedDict


class BaseQueryHandler(object):

    def __init__(self, command, query):
        
        self.query_data = dict()
        self.query_data['original_query'] = query.split(command)[1].strip()
        self.search_parameters = OrderedDict()

        self.msg_handler = None
        self.results_data = dict()

        self.AWAITING_REPLY = 0

    def select(self, keys, item_list):
        """Select items from item_list that contain all keys"""

        if type(keys) == str:
            keys = keys.split()
        
        if len(keys) == 1:
            try:
                return [item_list[int(keys[0])-1]]
            except:
                pass

        # itm[0] contains the data with which user is making selection
        results = [itm for itm in item_list if all([k in itm[0] for k in keys])]
        
        return results

    def narrow_parameters(self, message):
        """Narrow down list of data based on words in message"""

        if self.AWAITING_REPLY:
            for key, val in self.search_parameters.items():
                if type(val) == list:
                    self.search_parameters[key] = self.select(message, val)
                    break

    def get_reply(self):
        """Returns reply based on state"""

        for key, value in self.search_parameters.items():
            if type(value) == str:
                pass
            elif len(value) == 1:
                self.AWAITING_REPLY = 0
                self.finalize_params(key)
            else:
                self.AWAITING_REPLY += 1
                msg_handler = self.prepare_message_handler(key=key)
                reply = msg_handler.make_reply()
                return reply

        self.AWAITING_REPLY = 0
        resolved_query = self.resolve_query()

        msg_handler = self.prepare_message_handler(results=resolved_query)
        reply = msg_handler.make_reply()
        return reply

    def prepare_message_handler(self, results=None, key=None):
        """Create and return a MessageHandler with query results"""

        if not results:
            results = [itm[0] for itm in self.search_parameters[key]]

        message_data = {'msg_num': self.AWAITING_REPLY,
                        'results': results,
                        'query': self.query_data.get(key)}

        msg_handler = self.msg_handler(**message_data)

        return msg_handler
