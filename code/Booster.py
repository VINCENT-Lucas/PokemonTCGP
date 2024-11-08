class Booster:
    def __init__(self, name):
        self.name = name
        self.list_cards = []
        self.proba_cards = {}

    def set_probas(self, probas_dic):
        self.proba_cards = probas_dic
    
    def set_cards(self, cards_list):
        self.list_cards = cards_list
    