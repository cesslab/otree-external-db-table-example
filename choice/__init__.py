import random
from otree.api import *
from db.database import create_database_tables
from db.crud import get_ancestor_players, add_player_history


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'choice'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    ROW_PLAYER = 1
    COLUMN_PLAYER = 2
    TYPES = {1: 'Row Player', 2: 'Column Player'}


def creating_session(subsession):
    """Randomly assigns player roles with equal number type row and column. Each player is also randomly
     matched with an ancestor of the same role type in the session specified by the session config variable
     `ancestor_session_id`. If the ancestor session id is 0, then no ancestor is assigned to the player.
    """
    if subsession.round_number == 1:
        create_database_tables()

        players = subsession.get_players()
        half_num_players = len(players) // 2
        ancestor_session_id = subsession.session.config['ancestor_session_id']
        ancestor_players = get_ancestor_players(ancestor_session_id)

        # Create a list of roles, one for each player, with an equal share of row and column types, and shuffle it
        roles = [C.ROW_PLAYER] * half_num_players + [C.COLUMN_PLAYER] * half_num_players
        random.shuffle(roles)

        for p, role_type in zip(players, roles):
            p.role_type = role_type
            if ancestor_session_id > 0:
                # Filter players by role
                ancestor_role_players = [player for player in ancestor_players if player.role_type == role_type]
                # Randomly select a player one of the players that share the same role
                ancestor = random.choice(ancestor_role_players)
                # Remove the selected player from the list of ancestors
                ancestor_players.remove(ancestor)

                p.ancestor_session_id = ancestor.session_id
                p.ancestor_participant_id = ancestor.participant_id
                p.ancestor_advice = ancestor.advice



class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    role_type = models.IntegerField(choices=[[1, 'Row player'], [2, 'Column player']])
    choice = models.IntegerField(choices=[[1, 'Cooperate'],[2, 'Defect']], label="Your choice")
    advice = models.LongStringField(label="Advice to next player")
    ancestor_advice = models.LongStringField(label="Advice to you", default="")
    ancestor_session_id = models.IntegerField(default=0)
    ancestor_participant_id = models.IntegerField(default=0)



# PAGES
class Choice(Page):
    form_model = "player"
    form_fields = ["choice", "advice"]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            row_player=dict(C=dict(C=3, D=0), D=dict(C=5, D=1)), 
            column_player=dict(C=dict(C=3, D=5), D=dict(C=0, D=1)),
            ancesor_session_id=player.ancestor_session_id,
            ancestor_advice=player.ancestor_advice,
            role_type = C.TYPES[player.role_type],
            )

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        add_player_history(player)

class Advice(Page):
    pass


page_sequence = [Choice]