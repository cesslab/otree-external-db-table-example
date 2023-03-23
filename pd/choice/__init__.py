from otree.api import *


doc = """
Your app description
"""

class C(BaseConstants):
    NAME_IN_URL = 'choice'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    choice = models.IntegerField(choices=[[1, 'Cooperate'],[2, 'Defect']], label="Your choice")
    advice = models.LongStringField(label="advice")



# PAGES
class Choice(Page):
    form_model = "player"
    form_fields = ["choice", "advice"]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(row_player=dict(C=dict(C=3, D=0), D=dict(C=5, D=1)), column_player=dict(C=dict(C=3, D=5), D=dict(C=0, D=1)))


class Advice(Page):
    pass


page_sequence = [Choice]
