import logging


class NodeFactory:
    @staticmethod
    def get_node(node):
        try:
            instance = node()
            return instance
        except Exception as ex:
            logging.getLogger(NodeFactory.__name__).log(logging.ERROR, ex)
        return None
