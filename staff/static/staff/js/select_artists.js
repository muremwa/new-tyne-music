/* 
Select artists
*/


const addSVG = '<svg class="artist-add-btn" xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48"><path d="M26 14h-4v8h-8v4h8v8h4v-8h8v-4h-8v-8zM24 4C12.95 4 4 12.95 4 24s8.95 20 20 20 20-8.95 20-20S35.05 4 24 4zm0 36c-8.82 0-16-7.18-16-16S15.18 8 24 8s16 7.18 16 16-7.18 16-16 16z"/></svg>';
const removeSVG = '<svg class="artist-remove-btn" xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48"><path d="M14 22v4h20v-4H14zM24 4C12.95 4 4 12.95 4 24s8.95 20 20 20 20-8.95 20-20S35.05 4 24 4zm0 36c-8.82 0-16-7.18-16-16S15.18 8 24 8s16 7.18 16 16-7.18 16-16 16z"/></svg>';
const modalIncludedArtists = document.getElementById('select-id-selected-artists');
const hideClass = 'visually-hidden';
let includedArtists = [];
let savedArtists = [];


/**
 * 
 * @param {HTMLLIElement} element 
 * @param {number} id 
 */
function addArtistToIncluded (element, id) {
    if (includedArtists.length === 0) {
        includedArtists = processArtists(modalIncludedArtists, true)
    };

    if (![...new Map(includedArtists).values()].includes(id.toString())) {
        modalIncludedArtists.appendChild(element);
    };

    includedArtists = processArtists(modalIncludedArtists, true)
};

/**
 * Give a div with artists and return a map of artists and IDS
 * @param {HTMLUListElement} homeDiv
 * @param {boolean} modal
 * @returns {array<String, Number>[]} Map with keys as name and value as ID
 */
function processArtists (homeDiv, modal) {
    const artists = [];

    if (homeDiv.children && homeDiv.children.length > 0) {
        if (modal) {
            [...homeDiv.children].forEach((child) => {
                const childOne = child.children[0];
                artists.push([childOne.innerText.replace(/\s\(.*?\)/g, ''), parseInt(childOne.dataset.arId)]);
            })
        } else {
            [...homeDiv.children].forEach((child) => artists.push([child.innerText, parseInt(child.dataset.arId)]));
        }
    };

    return artists
};


/**
 * 
 * @param {string} name 
 * @param {string} nameId 
 * @param {boolean} modal
 * @param {boolean} isAdd 
 * @return {HTMLLIElement}
 */
function createModalArtistDisplay (name, nameId, isAdd) {
    const li = document.createElement('li');
    li.classList.add('select-artist-name');
    li.innerHTML = isAdd? addSVG: removeSVG;
    const span_ = document.createElement('span');
    span_.dataset.arId = nameId;
    span_.innerText = `${name} (ID: ${nameId})`;
    li.prepend(span_);

    if (isAdd) {
        li.lastChild.addEventListener('click', () => {
            addArtistToIncluded(createModalArtistDisplay(name, nameId, false), nameId);
            li.remove();
        });
    } else {
        li.lastChild.addEventListener('click', () => {
            li.remove();
            includedArtists = processArtists(modalIncludedArtists, true);
        });
    };
    return li;
};


/**
 * 
 * @param {string} name 
 * @param {string} nameId 
 * @returns {HTMLLIElement}
 */
function creatPlainArtistDisplay (name, nameId) {
    const li = document.createElement('li');
    li.dataset.arId = nameId
    li.innerText = name;
    return li;
}


/**
 * 
 * @param {array<String, Number>[]} artistsMap
 * @param {boolean} forModal
 * @param {boolean} forAdd
 * @returns {array<HTMLLIElement>} an array of list elements
 */
function processArtistsDisplay (artistsMap, forModal, forAdd) {
    const artists = [];

    if (forModal) {
        artistsMap.forEach((arr) => artists.push(createModalArtistDisplay(arr[0], arr[1], forAdd)));
    } else {
        artistsMap.forEach((arr) => artists.push(creatPlainArtistDisplay(arr[0], arr[1])));
    }

    return artists;
};


function searchArtists (event_) {
    includedArtists = processArtists(modalIncludedArtists, true)
    const valueInput = event_.target;
    const paintDiv = document.getElementById('select-id-search-artists');
    const loadingGif = document.getElementById('load-artists');

    if (valueInput && valueInput.value && paintDiv && loadingGif) {
        paintDiv.innerHTML = '';
        loadingGif.classList.remove(hideClass);
        
        const searchOptions = {
            url: `${valueInput.dataset.searchArtistsUrl}?name=${valueInput.value}`,
            responseType: 'json',
            error: () => {
                loadingGif.classList.add(hideClass);
                paintDiv.innerHTML = '<div class="alert alert-danger">Error searching</div>'
            },
            success: (payload_) => {
                loadingGif.classList.add(hideClass);
                if (payload_.response) {
                    // remove already added results
                    const filteredResults = payload_.response.filter((result) => !includedArtists.map((ar) => ar[1]).includes(result[1]))
                    const artistsForDisplay = processArtistsDisplay(filteredResults, true, true)
                    artistsForDisplay.length > 0? artistsForDisplay.forEach((artist) => paintDiv.appendChild(artist)): paintDiv.innerHTML = `<div class="alert alert-warning">No results for "${valueInput.value}"</div>`;
                } else {
                    paintDiv.innerHTML = '<div class="alert alert-warning">No results</div>'
                };
            }
        }

        ajax.get(searchOptions);
    };  
};

const searchArtistsEvent = (event_) => {
    if (event_.key === 'Enter') {
        event_.preventDefault();
        searchArtists(event_);
    };
}

const saveBtnEvent = (event_) => {
    if (includedArtists.length > 0) {
        savedArtists = [...includedArtists];
        const editedArtistsDiv = document.getElementById('edited-artists');
        editedArtistsDiv.parentElement.classList.remove(hideClass);
        editedArtistsDiv.innerHTML = '';
        document.getElementById('artists-ids').value = savedArtists.map((arr) => arr[1]).join(',');
        processArtistsDisplay(savedArtists, false, false).forEach((element) => editedArtistsDiv.appendChild(element));
    }
    document.getElementById('modal-close-btn').click();
};


const selectArtistModal = document.getElementById('artists-modal');

if (selectArtistModal) {
    selectArtistModal.addEventListener('shown.bs.modal', (event_) => {
        // paint current artists
        const currentArtists = includedArtists.length > 0? includedArtists: processArtists(document.getElementById('current-artists'))
        processArtistsDisplay(currentArtists, true, false).forEach((d) => modalIncludedArtists.appendChild(d));

        // search for new artists
        const valueInput = document.getElementById('artist-name-search');
        valueInput.addEventListener('keydown', searchArtistsEvent);

        // save artists
        const saveBtn = document.getElementById('save-artists-btn');
        saveBtn.addEventListener('click', saveBtnEvent);
    });

    selectArtistModal.addEventListener('hidden.bs.modal', (event_) => {
        document.getElementById('select-id-selected-artists').innerHTML = '';
        document.getElementById('select-id-search-artists').innerHTML = '<div class="alert alert-info">search results appear here</div>';
        document.getElementById('artist-name-search').removeEventListener('keydown', searchArtistsEvent);
        document.getElementById('save-artists-btn').removeEventListener('click', saveBtnEvent);

        const savedIds = savedArtists.map((arr) => arr[1]);
        const inclIds = includedArtists.map((arr) => arr[1]);
        let saved = false;

        if (savedIds.length === inclIds.length && savedIds.every((id, index) => id === inclIds[index])) {
            saved = true;
        };

        if (saved) {
            [...document.getElementsByClassName('not-saved')].forEach((el) => el.classList.add(hideClass));
        } else {
            [...document.getElementsByClassName('not-saved')].forEach((el) => el.classList.remove(hideClass));
        };
    });
};