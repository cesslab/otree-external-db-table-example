# oTree External Database Table Example
The purpose of this example program is to show how an external table can be used to share data between seperate otree sessions.

## The problem 
oTree does not, as of version 5.10, provide a method for sharing data across sessions (e.g. sharing advice between the first and eight session). 

## The Solution
A solution to this problem is to leverage the existing oTree database by adding a custom table to it which can be used to store and retrieve data across sessions.

## The Example Program
The example solution for this problem is implmented in a simple Prisoner's Dilemma with intergenerational advice. The game consists of two player groups randomly assigned the role of a row player or column player. Each player is show a choice screen which contains: 
- A payoff matrix
- Advice from an equivalent role player in the previous session, if not in the first session.
- A option to select cooperate or defect
- A continue button

After all players have made their choices they will see a final payoff screen.

## Implementation Description
### The `db` Directory
The `db` directory contains the primary code used to implement this solution.
```
│   ├── __init__.py
│   ├── crud.py (The functions used to add and read data in the custom database table)
│   ├── database.py (Initializes the database, and contains the table creation function)
│   └── models.py (Contains the models for the database table)
```

#### `crud.py`
The `crud.py` file contains the functions that read and save the player history data to the database.
```python
def add_player_history(player):
    """Add player history to database"""
    session = Session()

    player_history = PlayerHistory(
        session_id=player.session.id,
        participant_id=player.participant.id,
        role_type=player.role_type,
        choice=player.choice,
        advice=player.advice,
        ancestor_session_id=player.ancestor_session_id,
        ancestor_participant_id=player.ancestor_participant_id,
        ancestor_advice=player.ancestor_advice,
    )
    session.add(player_history)
    session.commit()
    session.close()

def get_ancestor_players(ancestor_session_id):
    """Get all players in a session with a specific role"""
    session = Session()
    histories = (
        session.query(PlayerHistory)
        .filter(PlayerHistory.session_id == ancestor_session_id)
        .all()
    )
    session.close()
    return histories
```

#### `database.py`
The `database.py` file initializes the references to the database and contains the function that creates the database.
```python
# The base directory should be two levels up from the current file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# The database url is either the environment variable DATABASE_URL or a local sqlite database
SQLITE_DATABASE_URL = 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')
# Create the database engine
engine = create_engine(os.getenv("DATABASE_URL", SQLITE_DATABASE_URL))
# Create a session factory
Session = sessionmaker(bind=engine)
# Create a base class for models
Base = declarative_base()

@staticmethod
def create_database_tables():
    """ Conditionally create database tables if they don't already exist """
    # Prevents unnecessary sql statements from being executed if the tables already exist
    if not engine.dialect.has_table(engine, "player_history"):
        Base.metadata.create_all(engine)
```

#### `models.py`
The `models.py` file contains the model used to create, read, and update the database table for sharing data across sessions. If you wanted to incorperate this into your own project you would have to modify this file and edit the existing sqlalchemy model or addA your own. Otree version 5.10 uses SQLAlchemy version 1.3.22 the documentation for this version can be found [here](https://docs.sqlalchemy.org/en/13/).
```python
from .database import Base 
from sqlalchemy import Column, Integer, String


class PlayerHistory(Base):
    """Player history model"""
    __tablename__ = "player_history"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer)
    participant_id = Column(Integer)
    role_type = Column(Integer)
    choice = Column(Integer)
    advice = Column(String)
    ancestor_session_id = Column(Integer, default=0)
    ancestor_participant_id = Column(Integer, default=0)
    ancestor_advice = Column(String, default="")
```

### The `__init__.py` File
The key parts of the `__init__.py` file is the `creating_session` function, which assigns the player's role, and also pairs each player to a player history depending on their role and the `ancestor_session_id` specified in the `settings.py` file.
```python
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
```

Another important section of the `__init__.py` file is the `Choice` page. In particular the `app_after_this_page` function in the `Choice` class which is used to save the player's history to the database.
```python
class Choice(Page):
    form_model = "player"
    form_fields = ["choice", "advice"]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            payoff_matrix=C.ROW_PAYOFF_MATRIX if player.role_type == C.ROW_PLAYER else C.COLUMN_PAYOFF_MATRIX,
            ancesor_session_id=player.ancestor_session_id,
            ancestor_advice=player.ancestor_advice,
            role_type = C.TYPES[player.role_type],
            )

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        add_player_history(player)
```

#### The `settings.py` file
The `settings.py` file contains the `ancestor_session_id` parameter that will be used to retrieve the player history for the current session. The default value is 0, in this case there is no history (i.e. The first session of the experiment or treatment.) This parameter is set in the `SESSION_CONFIGS`.
```python
SESSION_CONFIGS = [
    dict(
        name='pd_history',
        app_sequence=['choice'],
        num_demo_participants=1,
        ancestor_session_id=0,
    ),
]
```
