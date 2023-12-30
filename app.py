import datetime
import json
import requests
from tools import *
from flask import *
from model import *
import re

run_db()

app = Flask(__name__)
app.secret_key = 'fu388D8WRmXH8eLJ6N6km4uh'
year = datetime.datetime.now().year

NOTIF_AJOUT = "1041103551751004161"
DEV_YF = "1086356117430485192"
YUKIFLIX_AJOUTS = "https://discord.com/api/webhooks/1130964248370090115/6u4N8Hz7NsYBx5cHDBdoKnETtEUqHokzBBW2Ppl8nYq6j0x8OTngidOT7DUvXofeEKjP"
YUKIFLIX_REPORTS = "https://discord.com/api/webhooks/1170687176871251968/s_i7GrAPcJlLwvMcqcB6-F1kMM6HKy6w3-JTZVkPwPwPaTFlp2EYF2jRYKP4IvkD66oS"

@app.after_request
def after_request(response):
    close_db()
    return response

@app.before_request
def define_ephemeral_variable():
    g.year = year
    g.url = request.path
    user_id = session.get("user_id")
    if "admin" in request.path:
        if not user_id:
            # Rediriger vers la page de connexion si l'utilisateur n'est pas connecté
            return redirect('/login')

        # Récupérer l'objet Account correspondant à partir de l'ID de l'utilisateur
        account = session_account.query(Account).get(user_id)

        # Vérifier les autorisations de l'utilisateur
        if account.pseudo not in ["Honekichi", "Jojokes"]:
            return redirect("/")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404_error.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500_error.html'), 500
# ----

@app.route("/")
def accueil():
    count("visitor")

    # Récupérer toutes les séries et les films
    all_media = get_all_movies() + get_all_series()

    # Récupérer les noms de tous les films
    movies_names = get_all_movies_names()

    # Récupérer les noms de toutes les séries
    series_names = get_all_series_names()

    # Extraire les vues de chaque élément
    views = [int(media.view) for media in all_media]

    # Extraire les noms de tous les médias
    all_media_names = [media.name for media in all_media]

    # Trier les noms de médias par nombre de vues (en ordre décroissant)
    sorted_media_names_by_views = [name for _, name in sorted(zip(views, all_media_names), reverse=True)]

    # Initialiser une liste pour stocker les médias triés
    sorted_media = []

    # Parcourir les médias triés par vues
    for name in sorted_media_names_by_views:
        # Récupérer le média correspondant (film ou série)
        media = get_movie(name) if name in movies_names else get_serie(name)

        # Ajouter le média à la liste s'il existe
        if media:
            sorted_media.append(media)

    # Mettre à jour la liste triée des médias
    all_media = sorted_media
    top = format_liste_with_limit(all_media, 0, 10)

    user_id = session.get('user_id')
    account = session_account.query(Account).get(user_id)

    return render_template("index.html", len=len, nb_visit=read("visitor"), logged_in=True, account=account,
                           get_counter=get_counter,
                           get_all_movies_names=get_all_movies_names,
                           get_all_movies=get_all_movies, zip=zip,
                           get_all_series_names=get_all_series_names,
                           get_all_series=get_all_series,
                           get_all_movies_with_limit=get_all_movies_with_limit,
                           top=top)


@app.route('/search')
def search_results():
    query = request.args.get('q')

    if not query:
        title = "YukiFlix | Rechercher"
    else:
        title = f"{query} | YukiFlix"

    movie_results = session_movie.query(Movie).filter(
        Movie.name.ilike(f"%{query}%")).all()

    serie_results = session_serie.query(Serie).filter(
        Serie.name.ilike(f"%{query}%")).all()

    combined_results = movie_results + serie_results

    def relevance(item):
        return item.name.lower() == query.lower()

    combined_results.sort(key=relevance, reverse=True)

    search_label = f"Résultats pour '{query}'"

    results = {search_label: combined_results}

    user_id = session.get('user_id')
    account = session_account.query(Account).get(user_id)

    return render_template('search.html', query=query, search_results=results, title=title)


@app.route("/faq/")
def faq():
    user_id = session.get('user_id')
    account = session_account.query(Account).get(user_id)
    return render_template("faq.html", logged_in=True, account=account)

@app.route("/admin/")
def admin():
    seriesCount = len(get_all_series())
    usersCount = count_registered_users()
    moviesCount = len(get_all_movies())
    user_id = session.get('user_id')
    account = session_account.query(Account).get(user_id)
    return render_template("admin.html", logged_in=True, account=account, seriesCount=seriesCount, usersCount=usersCount, moviesCount=moviesCount)

@app.route("/admin/add/")
def add():
    user_id = session.get('user_id')
    account = session_account.query(Account).get(user_id)
    return render_template("add.html", logged_in=True, account=account)

@app.route("/admin/edit/")
def edit():
    user_id = session.get('user_id')
    account = session_account.query(Account).get(user_id)
    return render_template("edit.html", logged_in=True, account=account)


@app.route("/admin/delete/")
def delete():
    user_id = session.get('user_id')
    account = session_account.query(Account).get(user_id)
    return render_template("delete.html", logged_in=True, account=account)

@app.route("/admin/add/serie/", methods=["GET", "POST"])
def add_series():
    if request.method == "POST":
        name = get_input("name_serie")

        if name in series:
            error = "Cette série existe déjà"
            return render_template("add_serie.html", error=error)
        else:
                tt_episode = get_input("tt_episode")
                link_fr = get_input("link_serie_fr")
                link_vostfr = get_input("link_serie_vostfr")
                stars = get_input("star")
                description = get_input("description_serie")

                # img
                image_V = request.files["image_V"]
                image_H = request.files["image_H"]
                name_image_V = re.sub(r'[ :]+', '_', name)+"_V.webp"
                name_image_H = re.sub(r'[ :]+', '_', name)+"_H.webp"
                root_image_V = root_img + name_image_V
                root_image_H = root_img + name_image_H
                image_V.save(root_image_V)
                image_H.save(root_image_H)

                # push in db
                add_serie(name=name,description=description,stars=stars,
                          image_V=name_image_V, image_H=name_image_H)
                add_saison(name,1)
                add_episode(name_serie=name,saison_nb=1,epsiode_nb=1,name_episode=tt_episode,link_fr=link_fr,link_vostfr=link_vostfr)
                # discord notif
                notification_message = f"||<@&{NOTIF_AJOUT}>||\nNouvelle Série : **{name}**\nLien : https://yukiflix.pythonanywhere.com/watch/serie/{name.replace(' ', '%20')}"
                embed = {
                    "title": name,
                    "description": description,
                    "url": f"https://yukiflix.pythonanywhere.com/watch/serie/{name.replace(' ', '%20')}",
                    # Green color (you can use decimal or hex color code)
                    "color": 0x00FF00,
                    "image": {"url": "https://yukiflix.pythonanywhere.com/{root_image_H}"},
                }

                data = {"embeds": [embed], "content": notification_message}
                requests.post(YUKIFLIX_AJOUTS, data={
                              "content": notification_message})
                # ----
                return redirect(f"/watch/serie/{name}")

    user_id = session.get('user_id')
    account = session_account.query(Account).get(user_id)

    return render_template("add_serie.html", logged_in=True, account=account)


@app.route("/admin/add/serie/new/episode/", methods=["GET", "POST"])
def selected_serie():
    if request.method == "POST":
        serie = request.form.get("serie")
        return redirect("/add/serie/new/episode/" + serie)

    user_id = session.get('user_id')
    account = session_account.query(Account).get(user_id)
    return render_template("add_new_episode.html", name_series=get_all_series_names(), logged_in=True, account=account)


@app.route("/admin/add/serie/new/episode/<serie>", methods=["GET", "POST"])
def selected_season(serie):
    if request.method == "POST":
        season = get_input("season")
        return redirect(f"/add/serie/new/episode/{serie}/season/{season}")

    seasons = get_serie(serie).saisons

    user_id = session.get('user_id')
    account = session_account.query(Account).get(user_id)
    return render_template("add_new_episode2.html", seasons=seasons, serie=serie, logged_in=True, account=account)


@app.route("/admin/add/serie/new/episode/<serie>/season/<season>/", methods=["GET", "POST"])
def add_new_episode(serie, season):
    if request.method == "POST":

            # get inputs
            nb_episode = get_input("nb_episode")
            tt_episode = get_input("tt_episode")
            link_fr = get_input("link_fr")
            link_vostfr = get_input("link_vostfr")

            # push in db
            add_episode(name_serie=serie,saison_nb=int(saison),
                        epsiode_nb=nb_episode,name_episode=tt_episode,
                        link_fr=link_fr,link_vostfr=link_vostfr)


            return redirect(
                f"/watch/serie/{serie}/season/{season}/episode/{nb_episode}"
            )

    user_id = session.get('user_id')
    account = session_account.query(Account).get(user_id)
    return render_template("add_new_episode3.html", serie=serie, season=season, logged_in=True, account=account)

@app.route("/admin/add/serie/new/season/", methods=["GET", "POST"])
def selected_serie2():
    if request.method == "POST":
        serie = request.form.get("serie")
        return redirect(f"/add/serie/new/season/{serie}")

    user_id = session.get('user_id')
    account = session_account.query(Account).get(user_id)
    return render_template("add_new_saison1.html", name_series=get_all_series_names(), logged_in=True, account=account)

@app.route("/admin/add/serie/new/season/<serie>", methods=["GET", "POST"])
def add_serie_saison(serie):
    if request.method == "POST":
            # get inputs
            nb_saison = get_input("nb_saison")
            tt_episode = get_input("tt_episode")
            link_fr = get_input("link_fr")
            link_vostfr = get_input("link_vostfr")

            # push in db
            add_saison(serie, nb_saison)
            add_episode(name_serie=serie, saison_nb=nb_saison,
                        episode_nb=1,name_episode=tt_episode,link_fr=link_fr,link_vostfr=link_vostfr)

            return redirect(f"/watch/serie/" + serie)

    user_id = session.get('user_id')
    account = session_account.query(Account).get(user_id)
    return render_template("add_new_saison2.html", logged_in=True, account=account)


@app.route("/admin/add/movie/", methods=["GET", "POST"])
def add_movies():
    if request.method == "POST":
        name = get_input("name_movie")
        root_img = "static/img/"
        root_html = "templates/"
        password = get_input("password")
        error = "Ce film existe déjà" if name in get_all_movies_names() else "Ce n'est pas le bon mot de passe" if password != app.secret_key else ""
        if error:
            return render_template("add_movie.html", error=error)

        # inputs/main variables for db
        name_img = re.sub(r'[\s:]+|_+', '_', name)
        link_fr = get_input("link_movie_fr")
        link_vostfr = get_input("link_movie_vostfr")
        stars = get_input("star")
        description = get_input("description_movie")

        # images
        image_V = request.files["image_V"]
        image_H = request.files["image_H"]
        name_image_V = name_img + "_V.webp"
        name_image_H = name_img + "_H.webp"
        root_image_V = root_img+name_image_V
        root_image_H = root_img+name_image_H

        # saves images
        create_root(root_img)
        image_V.save(root_image_V)
        image_H.save(root_image_H)
        create_root(root_html)

        # push in db
        add_movie(name=name,description=description,image_H=name_image_H,image_V=name_image_V,stars=stars,link_fr=link_fr,link_vostfr=link_vostfr)

        # discord notif
        notification_message = f"||<@&{NOTIF_AJOUT}>||\nNouveau Film : **{name}**\nLien : https://yukiflix.pythonanywhere.com/watch/movie/{name.replace(' ', '%20')}"
        embed = {
            "title": name,
            "description": description,
            "url": f"https://yukiflix.pythonanywhere.com/watch/movie/{name.replace(' ', '%20')}",
            # Green color (you can use decimal or hex color code)
            "color": 0x00FF00,
            "image": {"url": f"https://yukiflix.pythonanywhere.com/{root_image_H}"},
        }

        data = {"embeds": [embed], "content": notification_message}

        response = requests.post(YUKIFLIX_AJOUTS, json=data)
        # ----

        # redirect
        return redirect("/")
    user_id = session.get('user_id')
    account = session_account.query(Account).get(user_id)
    return render_template("add_movie.html", logged_in=True, account=account)

@app.route("/watch/movie/count/<name>")
def count_click_movies(name):
    count(name)
    return redirect(f"/watch/movie/{name}")

@app.route("/watch/movie/<name>/")
def watch_movie(name):
    user_id = session.get('user_id')
    account = session_account.query(Account).get(user_id)
    if name in get_all_movies_names():
        return render_template("watch/movie/model.html", name=name,
                               logged_in=True, account=account,
                               movie=get_movie(name))

@app.route("/watch/serie/count/<name>")
def count_click_series(name):
    count(name)
    return redirect(f"/watch/serie/{name}")

@app.route("/watch/serie/<name>")
def watch_serie(name):
    user_id = session.get('user_id')
    account = session_account.query(Account).get(user_id)
    root = "/static/img/"
    return render_template("watch/serie/model.html", name=name,
                           logged_in=True, account=account,
                           get_serie=get_serie,
                           get_all_saisons=get_all_saisons,
                           get_all_episodes=get_all_episodes,
                           get_all_saisons_names=get_all_saisons_names,
                           zip=zip)

@app.route("/watch/serie/<name>/season/<saison>/episode/<episode>")
def watch_episode(name, saison, episode):
    user_id = session.get('user_id')
    account = session_account.query(Account).get(user_id)
    saison_bin = get_all_saisons_names(name).index(saison)+1

    titles_episodes = get_all_episodes_names(name)
    index_episode = int(episode)
    next_episode = index_episode+1 if index_episode < len(titles_episodes)-1 else index_episode
    next_episode = f"/watch/serie/{name}/season/{saison}/episode/{next_episode}"
    previous_episode = index_episode-1 if index_episode > 1 else index_episode
    previous_episode = f"/watch/serie/{name}/season/{saison}/episode/{previous_episode}"

    titles_saisons = get_all_saisons_names(name)
    index_saison = titles_saisons.index(saison)
    next_saison = index_saison+1 if index_saison < len(titles_saisons)-1 else index_saison
    next_saison = f"/watch/serie/{name}/season/{titles_saisons[next_saison]}/episode/1"
    previous_saison = index_saison-1 if index_saison > 1 else index_saison
    previous_saison = f"/watch/serie/{name}/season/{titles_saisons[previous_saison]}/episode/1"
    episode = get_episode_with_nb(name,saison,episode)
    try:
        if " " in episode.link_fr:
            episode.link_fr = '='.join(episode.link_fr.split('=')[1:]).replace(' ','').replace("\n","")
    except:
        pass
    try:
        if " " in episode.link_vostfr:
            episode.link_vostfr = '='.join(episode.link_vostfr.split('=')[1:]).replace(' ','').replace("\n","")
    except:
        pass
    return render_template(
        "watch/serie/watch_episode.html",
        name=name,
        saison=saison_bin,
        episode=episode,
        int=int,
        len=len,
        str=str,
        logged_in=True, account=account,
        get_serie=get_serie,
        get_all_episodes=get_all_episodes,
        get_saison=get_saison,
        index_episode=index_episode,
        index_saison=index_saison,
        get_all_saisons=get_all_saisons,
        get_episode_with_name=get_episode_with_name,
        next_saison=next_saison,
        next_episode=next_episode,
        previous_episode=previous_episode,
        previous_saison=previous_saison,
        get_episode_with_nb=get_episode_with_nb
    )

@app.route("/catalog/note/<nb_film>")
@app.route("/catalog/view/<nb_film>")
@app.route("/catalog/alphabet/<nb_film>")
@app.route("/catalog/<nb_film>")
@app.route("/catalog/")
def catalog(nb_film=None):
    user_id = session.get('user_id')
    account = session_account.query(Account).get(user_id)
    len_movies = len(get_all_movies())
    len_pages = len_movies//12
    page = 0
    movies = get_all_movies_with_limit(0,12)
    if not nb_film:
        return redirect("/".join(request.path.split("/")[:-1])+"/1")
    if nb_film:
        if nb_film.isdigit():
            nb_film = int(nb_film)-1
            page = nb_film+1
            nb_film *= 12
            if "alphabet" in request.path:
                movies = get_all_movies_specific_sorted_with_limit(nb_film, nb_film+12, abc=True)
            elif "view" in request.path:
                movies = get_all_movies_specific_sorted_with_limit(nb_film, nb_film+12, views=True)
            elif "note" in request.path:
                movies = get_all_movies_specific_sorted_with_limit(nb_film, nb_film+12, stars=True)
            else:
                movies = get_all_movies_specific_sorted_with_limit(nb_film, nb_film+12)
        else:
            return redirect("/catalog/1")
    else:
        return redirect("/catalog/1")
    return render_template("catalog.html", logged_in=True, account=account,
                           get_counter=get_counter,
                           get_all_series_names=get_all_series_names,
                           get_all_series=get_all_series,
                           zip=zip,
                           movies=movies,
                           len_movies=len_movies,
                           range=range,
                           page=page,
                           str=str,
                           redirect=redirect,
                           len_pages=len_pages)

@app.route("/login/", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect("/")

    if request.method == "POST":
        pseudo = get_input("username")
        password = get_input("password")

        # Vérification des informations d'identification dans la base de données
        account = verif_account(pseudo, password)
        if account:
            # Stocker l'ID de l'utilisateur dans la session au lieu de l'objet Account
            session['user_id'] = account.id
            return redirect("/")
        else:
            # Si les informations sont incorrectes, afficher un message d'erreur
            error_login = "Le nom d'utilisateur ou le mot de passe est incorrect. Veuillez réessayer."
            return render_template("login.html", error_login=error_login)

    return render_template("login.html")

@app.route("/register/", methods=["GET", "POST"])
def register():
    error_register = None

    if session.get("user_id"):
        return redirect("/")

    if request.method == "POST":
        # Récupérer les entrées du formulaire
        pseudo = request.form.get("username")
        password = request.form.get("password")

        # Vérifier si le compte existe déjà
        if verif_name(pseudo):
            error_register = "Ce nom d'utilisateur existe déjà."
        else:
            # Créer un nouveau compte et le sauvegarder
            account = Account(pseudo, password)
            add_account(pseudo, password)
            session['user_id'] = account.id  # Stocker l'ID de l'utilisateur dans la session

            # Redirection après l'inscription
            return redirect("/login")

    return render_template("register.html", error_register=error_register)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')

@app.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    # Récupérer l'objet Account correspondant à partir de l'ID de l'utilisateur
    account = session_account.query(Account).get(user_id)

    return render_template('profile.html', logged_in=True, account=account)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
