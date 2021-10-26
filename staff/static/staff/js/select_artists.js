/* 
    Select artists isolated for each modal
    There had to be need of these modals to appear twice or more on a page🤦🏾‍♂️
*/


const modalUtils = {
    addSvg: '<svg class="artist-add-btn" xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48"><path d="M26 14h-4v8h-8v4h8v8h4v-8h8v-4h-8v-8zM24 4C12.95 4 4 12.95 4 24s8.95 20 20 20 20-8.95 20-20S35.05 4 24 4zm0 36c-8.82 0-16-7.18-16-16S15.18 8 24 8s16 7.18 16 16-7.18 16-16 16z"/></svg>',
    removeSVG: '<svg class="artist-remove-btn" xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48"><path d="M14 22v4h20v-4H14zM24 4C12.95 4 4 12.95 4 24s8.95 20 20 20 20-8.95 20-20S35.05 4 24 4zm0 36c-8.82 0-16-7.18-16-16S15.18 8 24 8s16 7.18 16 16-7.18 16-16 16z"/></svg>',
    hideClass: 'visually-hidden',

    /**
     * Give a div with artists and return a array of arrays such that => [[name, ID], [name, ID]...] of artists and IDS
     * @param {HTMLUListElement} homeDiv
     * @param {boolean} modal
     * @returns {array<String, Number>[]} array of arrays such that => [[name, ID], [name, ID]...]
     */
    processArtists: (homeDiv, modal) => {
        const artists = [];

        if (homeDiv.children && homeDiv.children.length) {
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
    },
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
     * Add a result to staging area and save it to stage array
     * @param {string} name 
     * @param {number} artistId 
     * @param {HTMLUListElement} stageArea 
     * @param {[string, number][]} stageArray 
     * @param {() => void} stageArrayUpdater 
     */
    stageResultArtist: (name, artistId, stageArea, stageArray, stageArrayUpdater) => {
        // make sure the artist isn't in the staging area already
        if (!stageArray.map((arr) => arr[1]).includes(artistId)) {
            // create the element
            stageArea.appendChild(modalUtils.createModalArtistForDisplay(name, artistId, false, stageArray, stageArrayUpdater, stageArea));
            stageArrayUpdater();
        };
    },

    /**
     * Create a html element for display in the modal
     * @param {string} name 
     * @param {number} nameId 
     * @param {boolean} forAdd
     * @param {[string, number][]} arrayForStaging
     * @param {() => void} arrayForStagingUpdater
     * @param {HTMLUListElement} divForResults
     * @param {HTMLUListElement} divForStaging
     * @returns {HTMLLIElement}
     */
    createModalArtistForDisplay: (name, nameId, isAdd, arrayForStaging, arrayForStagingUpdater, divForStaging) => {
        const li = document.createElement('li');
        li.classList.add('select-artist-name');
        li.innerHTML = isAdd? modalUtils.addSvg: modalUtils.removeSVG;
        const span_ = document.createElement('span');
        span_.dataset.arId = nameId;
        span_.innerText = `${name} (ID: ${nameId})`;
        li.prepend(span_);

        if (isAdd) {
            li.lastChild.addEventListener('click', () => {
                li.remove();
                modalUtils.stageResultArtist(name, nameId, divForStaging, arrayForStaging, arrayForStagingUpdater);
            });
        } else {
            li.lastChild.addEventListener('click', () => {
                li.remove();
                arrayForStagingUpdater();
            });
        };

        return li;
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
     * 
     * @param {[string, number][]} rawArtists 
     * @param {boolean} forModal 
     * @param {boolean} forAdd 
     * @returns {HTMLLIElement[]}
     */
    processArtistsForDisplay: (rawArtists, forModal, forAdd, resultsStagingDiv, resultsStagingArray, updateStagingArray) => {
        const artists = [];

        if (forModal) {
            rawArtists.forEach((arr) => artists.push(
                modalUtils.createModalArtistForDisplay(arr[0], arr[1], forAdd, resultsStagingArray, updateStagingArray, resultsStagingDiv)
            ));
        } else {
            rawArtists.forEach((arr) => artists.push(
                modalUtils.creatPlainArtistForDisplay(arr[0], arr[1])
            ));
        };
        
        return artists;
    },

    /**
     * Search for artists
     * @param {string} query 
     * @param {string} searchUrl 
     * @param {HTMLImageElement} loadingGif 
     * @param {HTMLUListElement} resultsDiv 
     * @param {[string, number][]} stagedArtists
     * @param {HTMLUListElement} stageArea 
     */
    searchArtists: (query, searchUrl, loadingGif, resultsDiv, stagedArtists, stageArea, stagingArrayUpdater) => {
        if (query && searchUrl && loadingGif && resultsDiv) {
            resultsDiv.innerHTML = '';
            loadingGif.classList.remove(modalUtils.hideClass);

            const searchOptions = {
                url: `${searchUrl}?name=${query}`,
                responseType: 'json',
                error: () => {
                    loadingGif.classList.add(modalUtils.hideClass);
                    resultsDiv.innerHTML = '<div class="alert alert-danger">Error searching</div>'
                },
                success: (payload_) => {
                    loadingGif.classList.add(modalUtils.hideClass);
                    console.log(stagedArtists, "Search callback")

                    if (payload_.response) {
                        // remove duplicates
                        const results = payload_.response
                        const tempStageMap = new Map(stagedArtists.map((sa) => [...sa].reverse()));
                        const filteredResults = results.filter((result) => !tempStageMap.has(result[1]));

                        // paint the results
                        const resultElemets = modalUtils.processArtistsForDisplay(
                            filteredResults,
                            true,
                            true,
                            stageArea,
                            stagedArtists,
                            stagingArrayUpdater
                        );

                        if (resultElemets.length) {
                            resultElemets.forEach((result) => {
                                resultsDiv.appendChild(result)
                            });
                        } else {
                            resultsDiv.innerHTML = `<div class="alert alert-warning">No results for "${query}"</div>`;
                        };

                        delete tempStageMap;
                    } else {
                        resultsDiv.innerHTML = `<div class="alert alert-warning">No results for "${query}"</div>`;
                    };
                }
            }

            ajax.get(searchOptions);
        }
    },
        
};


const modals = document.getElementsByClassName('select-artists-modal-home');

[...modals].forEach((selectModal) => {
    let edited = false;
    let editingTurns = 0;
    let originalArtists = [];
    let stagingArtists = [];
    let savedArtists = [];
    const prefix = selectModal.dataset.prefixName;
    const elements = modalUtils.fetchHtmlElements(prefix);

    const updateStagingArray = () => {
        edited = true;
        stagingArtists = modalUtils.processArtists(elements.stagedArtistsDiv, true);
    };

    const searchCallback = (event_) => {
        if (event_.key === 'Enter') {
            event_.preventDefault();
            modalUtils.searchArtists(
                event_.target.value,
                event_.target.dataset.searchArtistsUrl,
                elements.loadingGif,
                elements.resultsDiv,
                stagingArtists,
                elements.stagedArtistsDiv,
                updateStagingArray
            );
        };
    };

    const saveBtnEvent = () => {
        savedArtists = [...stagingArtists];
        const editedArtists = modalUtils.processArtistsForDisplay(savedArtists, false, false);
        elements.editedArtistsDiv.innerHTML = ''
        elements.editedArtistsDiv.parentElement.classList.remove(modalUtils.hideClass);
        
        if (editedArtists.length) {
            elements.editedArtistsInput.value = savedArtists.map((chunk) => chunk[1]).join(',');
            editedArtists.forEach((element) => elements.editedArtistsDiv.appendChild(element));
        } else {
            elements.editedArtistsInput.value = '0';
            elements.editedArtistsDiv.innerHTML = '<div class="alert alert-danger">All artists removed</div>'
        };
        elements.closeBtn.click();
    };

    const resetBtnEvent = () => {
        elements.stagedArtistsDiv.innerHTML = '';
        modalUtils.processArtistsForDisplay(
            originalArtists,
            true,
            false,
            elements.stagedArtistsDiv,
            stagingArtists,
            updateStagingArray
        ).forEach((element) => elements.stagedArtistsDiv.appendChild(element));
        
        originalArtists = [];
        savedArtists = [];
        stagingArtists = [];
        editingTurns = 0;
        edited = false;

        elements.editedArtistsDiv.innerHTML = '';
        elements.editedArtistsInput.value = '';
        elements.editedArtistsDiv.parentElement.classList.add(modalUtils.hideClass);
        elements.notSaved.forEach((ns) => ns.classList.add(modalUtils.hideClass));
    };
    
    selectModal.addEventListener('shown.bs.modal', () => {
        editingTurns++;

        // save original artists
        if (editingTurns === 1) {
            originalArtists = modalUtils.processArtists(elements.currentArtists);
            stagingArtists = [...originalArtists];
        };

        // paint staged artists
        const stagedArtistElements = modalUtils.processArtistsForDisplay(stagingArtists, true, false, elements.stagedArtistsDiv, stagingArtists, updateStagingArray);
        stagedArtistElements.forEach((stagedArtist) => elements.stagedArtistsDiv.appendChild(stagedArtist));
        
        // search for artists
        elements.searchInput.addEventListener('keydown', searchCallback);

        // save artists
        elements.saveBtn.addEventListener('click', saveBtnEvent);

        // reset artists
        elements.resetBtn.addEventListener('click', resetBtnEvent);
        
        
    });
    
    selectModal.addEventListener('hidden.bs.modal', () => {
        elements.stagedArtistsDiv.innerHTML = '';
        elements.resultsDiv.innerHTML = '<div class="alert alert-info">search results appear here</div>'
        elements.searchInput.removeEventListener('keydown', searchCallback);
        elements.saveBtn.removeEventListener('click', saveBtnEvent);
        elements.resetBtn.removeEventListener('click', resetBtnEvent);

        const savedIds = savedArtists.map((arr) => arr[1]);
        const stagingIDS = stagingArtists.map((arr) => arr[1]);

        let saved = false;

        if (savedIds.length === stagingIDS.length && savedIds.every((id, index) => id === stagingIDS[index])) {
            saved = true;
        };

        if (edited) {
            if (saved) {
                elements.notSaved.forEach((ns) => ns.classList.add(modalUtils.hideClass));
            } else {
                elements.notSaved.forEach((ns) => ns.classList.remove(modalUtils.hideClass));
            };
        }

    })
});