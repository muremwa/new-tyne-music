/* 
    Selection of artists v3
    Uses OOP and isolates each modal as more than one may be included in a form.
    Also reduces the amount of arguments taken by functions
*/



/* Class to store info on selection of artists */
class ArtistsStore {
    /**
     * 
     * @param {string} name 
     * @param {number} id 
     * @param {[string, number][]} original 
     * @param {{
            modal: HTMLDivElement|null
            searchInput: HTMLInputElement|null
            loadingGif: HTMLImageElement|null
            resultsDiv: HTMLUListElement|null
            stagedArtistsDiv: HTMLUListElement|null
            resetBtn: HTMLButtonElement|null
            closeBtn: HTMLButtonElement|null
            saveBtn: HTMLButtonElement|null
            currentArtists: HTMLUListElement|null
            editedArtistsInput: HTMLInputElement|null
            editedArtistsDiv: HTMLUListElement|null
            notSaved: HTMLElement[]
        }} elements
     */
    constructor (name, id, original, elements) {
        if (!(name || id || original || stageDiv  || this.isArray(original))) {
            throw new Error("Something's wrong");
        }
        this.name =  name;
        this.id = id;
        this.originalArtists = [...original];
        this.stagedArtists = [...this.originalArtists];
        this.savedArtists = [];
        this.elements = elements;
        this.edited = false;
        this.saved = true;
    };

    isArray(arraySuspect) {
        return Array.isArray(arraySuspect);
    };

    /**
     * Stage a new artist
     * @param {[string, number][]} artists 
     */
    stage (artists, callback) {
        if (!this.isArray(artists)) {
            throw new Error('artists is not an array')
        }
        this.stagedArtists = [...artists];
        this.edited = true;
        this.saved = false;
        callback();
    };

    refreshStage () {
        const artists = modalFuncs.processArtistsFromHTML(this.elements.stagedArtistsDiv, true);
        this.stage(artists, () => {
            if (!artists.length) {
                this.elements.stagedArtistsDiv.innerHTML = modalConstants.emptyStage;
            };
        });
        return artists;
    };

    /**
     * Save the staged artists
     * @param {(savedArtists: [string, number]) => void} callback 
     */
    save (callback) {
        this.savedArtists = [...this.stagedArtists];
        this.edited = false;
        this.saved = true;
        callback(this.savedArtists);
    };

    /**
     * Clear to start afresh
     * @param {(originalArtists: [string, number][]) => void} callback 
     */
    clear (callback) {
        this.stagedArtists = [...this.originalArtists];
        this.savedArtists = [];
        this.saved = true;
        this.edited = false;
        callback(this.originalArtists);
    };
};


/* Constants to help in selection */
const modalConstants = {
    addSvg: '<svg class="artist-add-btn" xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48"><path d="M26 14h-4v8h-8v4h8v8h4v-8h8v-4h-8v-8zM24 4C12.95 4 4 12.95 4 24s8.95 20 20 20 20-8.95 20-20S35.05 4 24 4zm0 36c-8.82 0-16-7.18-16-16S15.18 8 24 8s16 7.18 16 16-7.18 16-16 16z"/></svg>',
    removeSVG: '<svg class="artist-remove-btn" xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48"><path d="M14 22v4h20v-4H14zM24 4C12.95 4 4 12.95 4 24s8.95 20 20 20 20-8.95 20-20S35.05 4 24 4zm0 36c-8.82 0-16-7.18-16-16S15.18 8 24 8s16 7.18 16 16-7.18 16-16 16z"/></svg>',
    hideClass: 'visually-hidden',
    emptyStage: '<div class="alert alert-info">Staged artists appear here</div>',
    emptyResults: '<div class="alert alert-info">search results appear here</div>',
    emptyEditedArtists: '<div class="alert alert-danger">All artists removed</div>'
};


/* Functions to help in the selection */
const modalFuncs = {
        /**
     * Get all required HTML elements
     * @param {string} prefix 
     * @returns {{
        modal: HTMLDivElement|null
        searchInput: HTMLInputElement|null
        loadingGif: HTMLImageElement|null
        resultsDiv: HTMLUListElement|null
        stagedArtistsDiv: HTMLUListElement|null
        resetBtn: HTMLButtonElement|null
        closeBtn: HTMLButtonElement|null
        saveBtn: HTMLButtonElement|null
        currentArtists: HTMLUListElement|null
        editedArtistsInput: HTMLInputElement|null
        editedArtistsDiv: HTMLUListElement|null
        notSaved: HTMLElement[]
     }}
     */
     fetchHtmlElements: (prefix) => ({
        modal: document.getElementById(`${prefix}-artists-modal`),
        searchInput: document.getElementById(`${prefix}-artist-name-search`),
        loadingGif: document.getElementById(`${prefix}-load-artists`),
        resultsDiv: document.getElementById(`${prefix}-select-id-search-artists`),
        stagedArtistsDiv: document.getElementById(`${prefix}-select-id-selected-artists`),
        resetBtn: document.getElementById(`${prefix}-modal-reset-btn`),
        closeBtn: document.getElementById(`${prefix}-modal-close-btn`),
        saveBtn: document.getElementById(`${prefix}-save-artists-btn`),
        currentArtists: document.getElementById(`${prefix}-current-artists`),
        editedArtistsInput: document.getElementById(`${prefix}-artists-ids`),
        editedArtistsDiv: document.getElementById(`${prefix}-edited-artists`),
        notSaved: [...document.getElementsByClassName(`${prefix}-not-saved`)]
    }),

    /**
     * Give a div with artists and return a array of arrays such that => [[name, ID], [name, ID]...] of artists and IDS
     * @param {HTMLUListElement} homeDiv
     * @param {boolean} modal
     * @returns {array<String, Number>[]} array of arrays such that => [[name, ID], [name, ID]...]
    */
    processArtistsFromHTML: (homeDiv, modal) => {
        const artists = [];

        if (homeDiv.children && homeDiv.children.length) {
            if (modal) {
                [...homeDiv.children].forEach((child) => {
                    if (child.tagName === 'LI') {
                        const childOne = child.children[0];
                        artists.push([childOne.innerText.replace(/\s\(.*?\)/g, ''), parseInt(childOne.dataset.arId)]);
                    };
                })
            } else {
                [...homeDiv.children].forEach((child) => {
                    if (child.tagName === 'LI') {
                        artists.push([child.innerText, parseInt(child.dataset.arId)]);
                    };
                });
            }
        };

        return artists
    },

    /**
     * HTML element for the plane
     * @param {string} name 
     * @param {number} nameId 
     * @returns {HTMLLIElement}
     */
     creatPlainArtistForDisplay: (name, nameId) => {
        const li = document.createElement('li');
        li.dataset.arId = nameId
        li.innerText = name;
        return li;
    },

    /**
     * Create a LI element
     * @param {string} name 
     * @param {number} nameid 
     * @param {boolean} isAdd
     * @param {ArtistsStore} manager 
     * @returns {HTMLLIElement}
     */
    createModalArtistDisplay: (name, nameId, isAdd, manager) => {
        const li = document.createElement('li');
        li.classList.add('select-artist-name');
        li.innerHTML = isAdd? modalConstants.addSvg: modalConstants.removeSVG;
        const span_ = document.createElement('span');
        span_.dataset.arId = nameId;
        span_.innerText = `${name} (ID: ${nameId})`;
        li.prepend(span_);

        if (isAdd) {
            if (!manager.stagedArtists.map((chunk) => chunk[1]).includes(nameId)) {
                li.lastChild.addEventListener('click', () => {
                    li.remove();

                    if (manager.stagedArtists.length === 0) {
                        manager.elements.stagedArtistsDiv.innerHTML = '';
                    };

                    manager.elements.stagedArtistsDiv.appendChild(
                        modalFuncs.createModalArtistDisplay(name, nameId, false, manager)
                    );
                    manager.refreshStage();
                });
            };        
        } else {
            li.lastChild.addEventListener('click', () => {
                li.remove();
                manager.refreshStage();
            });
        };
        return li
    },

    /**
     * Process li elements for the staging area
     * @param {ArtistsStore} manager 
     * @returns {HTMLLIElement[]}
     */
    processStageArtists: (manager) => manager.stagedArtists.map((chunk) => modalFuncs.createModalArtistDisplay(chunk[0], chunk[1], false, manager)),
    
    /**
     * Process li elements for the results area
     * @param {[string, number][]} results 
     * @param {ArtistsStore} manager 
     * @returns {HTMLLIElement[]}
     */
    processResultArtists: (results, manager) => results.map((chunk) => modalFuncs.createModalArtistDisplay(chunk[0], chunk[1], true, manager)),

    /**
     * Process li elements for the edited area
     * @param {ArtistsStore} manager 
     * @returns {HTMLLIElement[]}
     */
    processEditedArtists: (manager) => manager.savedArtists.map((chunk) => modalFuncs.creatPlainArtistForDisplay(chunk[0], chunk[1])),

    /**
     * 
     * @param {string} query 
     * @param {string} searchUrl 
     * @param {ArtistsStore} manager 
     */
    searchForArtists: (query, searchUrl, manager) => {
        if (query && searchUrl && manager) {
            const noResultsError = `<div class="alert alert-warning">No results for "${query}"</div>`;
            manager.elements.resultsDiv.innerHTML = '';
            manager.elements.loadingGif.classList.remove(modalConstants.hideClass);

            const searchOptions = {
                url: `${searchUrl}?name=${query}`,
                responseType: 'json',
                error: () => {
                    manager.elements.loadingGif.classList.add(modalConstants.hideClass);
                    manager.elements.resultsDiv.innerHTML = '<div class="alert alert-danger">Error searching</div>';
                },
                success: (payload) => {
                    manager.elements.loadingGif.classList.add(modalConstants.hideClass);
                    if (payload.response) {
                        const results = payload.response
                        const tempStageMap = new Map(manager.stagedArtists.map((sa) => [...sa].reverse()));
                        const filteredResults = results.filter((result) => !tempStageMap.has(result[1]));

                        if (filteredResults.length) {
                            modalFuncs.processResultArtists(filteredResults, manager).forEach((element) => {
                                manager.elements.resultsDiv.appendChild(element)
                            });
                        } else {
                            manager.elements.resultsDiv.innerHTML = noResultsError;
                        };

                    } else {
                        manager.elements.resultsDiv.innerHTML = noResultsError;
                    };
                }
            };
            ajax.get(searchOptions);
        };
    },
};


/* 
Loop through all modals and listen for show and hide
*/
[...document.getElementsByClassName('select-artists-modal-home')].forEach((modal, modalIndex) => {
    const prefix = modal.dataset.prefixName;
    const modalEl = modalFuncs.fetchHtmlElements(prefix);
    const initArtists = modalFuncs.processArtistsFromHTML(modalEl.currentArtists);
    const manager = new ArtistsStore(prefix, modalIndex, initArtists, modalEl);
    modalEl.editedArtistsInput.value = '';

    /* Callback to initiate a search */
    /**
     * 
     * @param {Event} event_ 
     */
    const searchCallback = (event_) => {
        if (event_.key === 'Enter') {
            event_.preventDefault();
            modalFuncs.searchForArtists(event_.target.value, event_.target.dataset.searchArtistsUrl, manager);
        };
    };

    /* Callback to save staged artists */
    const saveBtnEvent = () => {
        manager.save((artists) => {
            modalEl.editedArtistsDiv.innerHTML = '';
            modalEl.editedArtistsDiv.parentElement.classList.remove(modalConstants.hideClass);
            
            if (artists.length) {
                modalEl.editedArtistsInput.value = manager.savedArtists.map((chunk) => chunk[1]).join(',');
                modalFuncs.processEditedArtists(manager).forEach((element) => modalEl.editedArtistsDiv.appendChild(element));
            } else {
                modalEl.editedArtistsInput.value = '0';
                modalEl.editedArtistsDiv.innerHTML = modalConstants.emptyEditedArtists;
            };

            modalEl.closeBtn.click();
        });
    };

    /* Reset artists selection modal */
    const resetBtnCallback = () => {
        manager.clear((ogArtists) => {
            if (ogArtists.length) {
                modalEl.stagedArtistsDiv.innerHTML = '';
                modalFuncs.processStageArtists(manager).forEach((item) => modalEl.stagedArtistsDiv.appendChild(item));
            } else {
                modalEl.stagedArtistsDiv.innerHTML = modalConstants.emptyStage;
            };
        });

        modalEl.editedArtistsDiv.parentElement.classList.add(modalConstants.hideClass);
        modalEl.editedArtistsInput.value = '';
        modalEl.notSaved.forEach((element) => element.classList.add(modalConstants.hideClass));
    };
    
    /* When a modal is opened */
    modal.addEventListener('shown.bs.modal', () => {
        // paint staged artists
        if (manager.stagedArtists.length) {
            modalEl.stagedArtistsDiv.innerHTML = '';
            modalFuncs.processStageArtists(manager).forEach((item) => modalEl.stagedArtistsDiv.appendChild(item));
        };
        
        // search for artists
        modalEl.searchInput.addEventListener('keydown', searchCallback);

        // save artists
        modalEl.saveBtn.addEventListener('click', saveBtnEvent);

        // reset artists
        modalEl.resetBtn.addEventListener('click', resetBtnCallback);


    });
    
    
    /* When a modal is closed */
    modal.addEventListener('hidden.bs.modal', () => {
        modalEl.stagedArtistsDiv.innerHTML = modalConstants.emptyStage;
        modalEl.resultsDiv.innerHTML = modalConstants.emptyResults;
        modalEl.searchInput.removeEventListener('keydown', searchCallback);
        modalEl.saveBtn.removeEventListener('click', saveBtnEvent);
        modalEl.resetBtn.removeEventListener('click', resetBtnCallback);

        // check if changes were saved
        if (manager.edited && !manager.saved) {
            modalEl.notSaved.forEach((element) => element.classList.remove(modalConstants.hideClass));
        } else {
            modalEl.notSaved.forEach((element) => element.classList.add(modalConstants.hideClass));
        };
    });

});