from model import *

"""
series_names = get_all_series_names()
movies_names = get_all_movies_names()
movies = get_all_movies()
series = get_all_series()
counts = get_all_counter()

for count in counts:
    try:
        name = count.name
        media = get_serie(name) if name in series_names else get_movie(name)
        media.view = count.count
    except:
        pass
session_serie.commit()
session_movie.commit()
"""

all_movies_stars = get_all_movies_with_limit(34)
for movie in all_movies_stars:
    movie.stars *= 2
session_movie.commit()
