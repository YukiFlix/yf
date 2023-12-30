const defaultMovies = Array.from(document.querySelectorAll('#animes-grid-movies .anime-card'));
const defaultSeries = Array.from(document.querySelectorAll('#animes-grid-series .anime-card'));
const popularAnimesGrid = document.getElementById('animes-grid-all');

function resetMoviesAndSeries(category) {
    const animesGrid = document.getElementById(`animes-grid-${category}`);
    const animes = Array.from(animesGrid.getElementsByClassName('anime-card'));
    const sortedAnimes = Array.from(animesGrid.getElementsByClassName('sorted'));
    sortedAnimes.forEach((anime) => animesGrid.removeChild(anime));
    animes.forEach((anime) => animesGrid.appendChild(anime));
}

function sortMoviesAndSeries(category, option, sortFunction) {
    const animesGrid = document.getElementById(`animes-grid-${category}`);
    const animes = Array.from(animesGrid.getElementsByClassName('anime-card'));
    if (option === 'default') {
        resetMoviesAndSeries(category);
        if (category === 'movies') defaultMovies.forEach((movie) => animesGrid.appendChild(movie));
        else if (category === 'series') defaultSeries.forEach((serie) => animesGrid.appendChild(serie));
    } else {
        animes.sort(sortFunction);
        resetMoviesAndSeries(category);
        animes.forEach((anime) => {
            anime.classList.add('sorted');
            animesGrid.appendChild(anime);
        });
    }
}

function sortByViews(a, b) {
    const viewsA = parseInt(a.querySelector('.views span').textContent);
    const viewsB = parseInt(b.querySelector('.views span').textContent);
    return viewsB - viewsA;
}

function sortByRating(a, b) {
    const ratingA = parseFloat(a.querySelector('.rating').dataset.star);
    const ratingB = parseFloat(b.querySelector('.rating').dataset.star);
    return ratingB - ratingA;
}

function sortByTitle(a, b) {
    const titleA = a.querySelector('.card-title').textContent.toLowerCase();
    const titleB = b.querySelector('.card-title').textContent.toLowerCase();
    return titleA.localeCompare(titleB);
}

function setupFilter(category) {
    document.querySelectorAll(`#${category} .filter-options input`).forEach((input) => {
        input.addEventListener('change', function () {
            const option = this.value;
            if (option === 'rating') sortMoviesAndSeries(category, option, sortByRating);
            else if (option === 'alphabetical') sortMoviesAndSeries(category, option, sortByTitle);
            else sortMoviesAndSeries(category, option);
        });
    });
}

setupFilter('movies');
setupFilter('series');
