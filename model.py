from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import *
from tools import *

engine_serie = create_engine('sqlite:///db/series.db', echo=True)

Session = sessionmaker(bind=engine_serie)

session_serie = Session()

# Déclarez une classe qui représente la table
base_serie = declarative_base()

# series
class Serie(base_serie):
    __tablename__ = "series"
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    description = Column(Text)
    stars = Column(Integer)
    image_V = Column(Text)
    image_H = Column(Text)
    view = Column(Integer)
    saisons = relationship("Saison", back_populates="serie")
    episodes = relationship("Episode", back_populates="serie")

class Saison(base_serie):
    __tablename__ = "saisons"
    id = Column(Integer, primary_key=True)
    nb = Column(Text)
    serie_id = Column(Integer, ForeignKey('series.id'))
    serie = relationship("Serie", back_populates="saisons")
    episodes = relationship("Episode", back_populates="saison")

class Episode(base_serie):
    __tablename__ = "episodes"
    id = Column(Integer, primary_key=True)
    nb = Column(Integer)
    link_fr = Column(Text)
    link_vostfr = Column(Text)
    name = Column(Text)
    serie_id = Column(Integer, ForeignKey('series.id'))
    saison_id = Column(Integer, ForeignKey('saisons.id'))
    saison = relationship("Saison", back_populates="episodes")
    serie = relationship("Serie", back_populates="episodes")

def get_all_series_sort_by_view():
    return session_serie.query(Serie).order_by(Serie.view).all()

def get_all_series_sort_by_view_with_limit(begin,limit):
    return format_liste_with_limit(get_all_series_sort_by_view(),begin,limit)

def verif_serie(name):
    return True if session_serie.query(Serie).filter_by(name=name).first() else False

def verif_saison(name_serie, nb):
    return True if session_serie.query(Saison).join(Serie).filter(Serie.name == name_serie, Saison.nb == nb).first() else False

def verif_episode(name, saison_nb,episode_name):
    return True if session_serie.query(Episode).join(Saison).join(Serie).filter(Serie.name == name,Saison.nb == saison_nb,Episode.name == episode_name).first() else False

def add_serie(name,description,stars,image_V,image_H):
    if verif_serie(name):
        print("la série existe déjà")
    else:
        serie = Serie(name=name, description=description, stars=stars, image_V=image_V, image_H=image_H)
        session_serie.add(serie)
        session_serie.commit()

def add_saison(name_serie, nb):
    if verif_saison(name_serie, nb):
        print("la saison existe déjà")
    else:
        serie = get_serie(name_serie)
        saison = Saison(nb=nb, serie=serie)
        session_serie.add(saison)
        session_serie.commit()

def serie_count(name):
    serie = get_serie(name_serie)
    serie.view += 1
    session_serie.commit()

def serie_read_count(name):
    return get_serie(name_serie).view

def add_episode(name_serie, nb, episode_nb, name_episode, link_fr=None, link_vostfr=None):
    if verif_episode(name_serie, nb,name_episode):
        print("l'épisode existe déjà")
    else:
        saison = get_saison(name_serie, nb)
        episode = Episode(nb=episode_nb, link_fr=link_fr, link_vostfr=link_vostfr, name=name_episode, saison=saison)
        session_serie.add(episode)
        session_serie.commit()

def get_serie(name):
    serie = session_serie.query(Serie).filter_by(name=name).first()
    if serie:
        return serie
    else:
        raise ErrorDB(f"La série {name} n'est pas dans la db")

def get_saison(serie_name,nb):
    serie = get_serie(serie_name)
    saison = session_serie.query(Saison).filter_by(serie=serie, nb=nb).first()
    if saison:
        return saison
    else:
        raise ErrorDB(f"La saison {nb} de la série {serie_name} n'est pas dans la db")

def get_episode_with_name(name,saison_nb,episode_name):
    episode = session_serie.query(Episode).join(Saison).join(Serie).filter(
        Serie.name == name,
        Saison.nb == saison_nb,
        Episode.name == episode_name
    ).first()
    if episode:
        return episode
    else:
        raise ErrorDB(f"Le nom de l'épisode {episode_name} de la saison {saison_nb} de la série {name} n'est pas dans la db")

def get_all_series():
    return session_serie.query(Serie).all()

def get_all_series_names():
    return [x.name for x in get_all_series()]

def get_all_saisons(name_serie):
    return get_serie(name_serie).saisons

def get_all_saisons_names(name_serie):
    return [x.nb for x in get_all_saisons(name_serie)]

def get_all_episodes(name_serie,saison_nb):
    return get_saison(name_serie,saison_nb).episodes

def get_all_episodes_names(name):
    return [episode.name for saison in get_serie(name).saisons for episode in get_all_episodes(name,saison.nb)]

def get_episode_with_nb(name,saison_nb,episode_nb):
    episode = session_serie.query(Episode).join(Saison).join(Serie).filter(
        Serie.name == name,
        Saison.nb == saison_nb,
        Episode.nb == episode_nb
    ).first()
    if episode:
        return episode
    else:
        raise ErrorDB(f"L'épisode {episode_nb} de la saison {saison_nb} de la série {name} n'est pas dans la db")

# movie
engine_movie = create_engine('sqlite:///db/movies.db', echo=True)
session_movie = sessionmaker(bind=engine_movie)
session_movie = session_movie()
base_movie = declarative_base()

class Movie(base_movie):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    description = Column(Text)
    image_V = Column(Text)
    image_H = Column(Text)
    link_fr = Column(Text)
    link_vostfr = Column(Text)
    stars = Column(Float)
    view = Column(Integer)

def get_all_movies_sort_by_stars():
    movies = get_all_movies()
    stars = [x.stars for x in movies]
    print(stars)
    _,movies = trier_2_listes(stars,movies)
    return movies[::-1]

def get_all_movies_sort_by_stars_with_limit(begin,limit):
    return format_liste_with_limit(get_all_movies_sort_by_stars(),begin,limit)

def get_all_movies_sort_by_view():
    return session_movie.query(Movie).order_by(Movie.view).all()

def get_all_movies_sort_by_view_with_limit(begin,limit):
    return format_liste_with_limit(get_all_movies_sort_by_view(),begin,limit)

def get_all_movies_sort_by_abc():
    return session_movie.query(Movie).order_by(Movie.name).all()

def get_all_movies_sort_by_abc_with_limit(begin,limit):
    return format_liste_with_limit(get_all_movies_sort_by_abc(),begin,limit)

def get_all_movies_with_limit(begin=0,limit=None):
    if not limit:
        limit = len(get_all_movies())-1
    return format_liste_with_limit(get_all_movies(),begin,limit)

def get_all_movies_specific_sorted_with_limit(begin, limit, abc=None, views=None, stars=None):
    if abc:
        return get_all_movies_sort_by_abc_with_limit(begin,limit)
    elif views:
        return get_all_movies_sort_by_view_with_limit(begin,limit)
    elif stars:
        return get_all_movies_sort_by_stars_with_limit(begin,limit)
    return get_all_movies_with_limit(begin,limit)

def delete_movie(name):
    movie = session_movie.query(Movie).filter_by(name=name).first()
    session_movie.delete(movie)
    session_movie.commit()

def get_movie(name):
    return session_movie.query(Movie).filter_by(name=name).first()

def movie_count(name):
    movie = get_movie(name)
    movie.view += 1
    session_movie.commit()

def movie_read_count():
    return get_movie(name).view

def get_all_movies():
    return session_movie.query(Movie).all()

def get_all_movies_names():
    return [x.name for x in get_all_movies()]


def add_movie(name, description, image_V, image_H, stars,link_fr=None,link_vostfr=None):
    movie = Movie(name=name,description=description,image_V=image_V,
                  image_H=image_H,link_fr=link_fr,link_vostfr=link_vostfr,
                  stars=stars)
    session_movie.add(movie)
    session_movie.commit()

# animes
def get_all_animes():
    return get_all_movies()+get_all_series()

def get_all_animes_names():
    return [x.name for x in get_all_animes()]

# counters
base_counter = declarative_base()
engine_counter = create_engine('sqlite:///db/counter.db', echo=True)

session_counter = sessionmaker(bind=engine_counter)

session_counter = session_counter()
class Counter(base_counter):
    __tablename__ = 'counters'
    id = Column(Integer, primary_key=True)
    count = Column(Integer, default=1)
    name = Column(Text)


def get_counter(name):
    return session_counter.query(Counter).filter_by(name=name).first()

def read(name):
    record = get_counter(name)
    return record.count if record else 0

def add_counter(name, count_value=1):
    new_counter = Counter(name=name, count=count_value)
    session_counter.add(new_counter)
    session_counter.commit()

def count(name):
    record = get_counter(name)
    if record:
        if record.count == 0:
            return add_counter(name, count_value=1)
        record.count += 1
        session_counter.commit()
    else:
        add_counter(name, count_value=1)

# accounts
base_account = declarative_base()
engine_account = create_engine('sqlite:///db/account.db', echo=True)

session_account = sessionmaker(bind=engine_account)

session_account = session_account()

class Account(base_account):
    __tablename__ = 'account'
    id = Column(Integer, primary_key=True)
    pseudo = Column(Text)
    password = Column(Text)

    def __init__(self, pseudo, password):
        self.pseudo = pseudo
        self.password = password

def add_account(pseudo,password):
    account = Account(pseudo=pseudo, password=password)
    session_account.add(account)
    session_account.commit()
    return account

def verif_password(password):
    return session_account.query(Account).filter_by(password=password).first()

def verif_name(pseudo):
    return session_account.query(Account).filter_by(pseudo=pseudo).first()

def verif_account(pseudo, password):
    return session_account.query(Account).filter_by(pseudo=pseudo, password=password).first()

def verif_pseudo(pseudo):
    return bool(Account.query.filter_by(pseudo=pseudo).first())

def get_id_by_password(password):
    account = Account.query.filter_by(password=password).first()
    return account.id if account else None

def get_id_by_pseudo(pseudo):
    account = Account.query.filter_by(pseudo=pseudo).first()
    return account.id if account else None

def count_registered_users():
    return session_account.query(Account).count()



def get_all_global_variables_name():
    return [x.split("=")[0].replace(" ","") for x in open(__file__,"r").read().split("\n") if "=" in x and x[:4] != "    "]

variables = get_all_global_variables_name()

def run_db():
    global variables
    for x,y in {v:[eval(x) for x in variables if "engine" in x][i] for i,v in enumerate([eval(x) for x in variables if "base" in x])}.items():
        x.metadata.create_all(y)

def close_db():
    global variables
    [eval(x).close() for x in variables if "session" in x]
