const genresField = document.getElementById('id_genres');
const genresHome = document.getElementById('edited-g');

/**
 * Write genres as list items to to a HTMLUList element (home)
 * @param {string[]} genres
 * @param {HTMLUListElement} home
 * @returns {void}
 */
function genreListSave (genres, home) {
    home.innerHTML = '';

    genres.forEach((genre) => {
        const l = document.createElement('li');
        l.innerText = genre;
        home.appendChild(l);
    });
};

if (genresField && genresHome) {
    genresField.addEventListener('change', (event_) => {
        const selectedGenres = [...genresField.selectedOptions].map((option) => option.innerText);
        genreListSave(selectedGenres, genresHome);
    });

    genresField.form.addEventListener('reset', () => genresHome.innerHTML = '');
};