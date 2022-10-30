/* Add nicknames */
const nicknamesModal = document.getElementById('nicknames-modal');
const nicknamesformInput = document.getElementById('id_nicknames');

if (nicknamesModal && nicknamesformInput) {
    const nonames = '<div class="alert alert-info">No nicknames yet</div>';
    const removeSVG = '<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48"><path d="M14 22v4h20v-4H14zM24 4C12.95 4 4 12.95 4 24s8.95 20 20 20 20-8.95 20-20S35.05 4 24 4zm0 36c-8.82 0-16-7.18-16-16S15.18 8 24 8s16 7.18 16 16-7.18 16-16 16z"/></svg>';
    const nicknamesInput = document.getElementById('nickname-input');
    const nicknamesHome = document.getElementById('nicknames-home');
    const savedNicknames = document.getElementById('saved-nicknames');
    const nicknames = nicknamesformInput.value.split(',').map((name) => name.trim()).filter((name) => Boolean(name));
    const originalNicknames = [...nicknames];

    const createNicknamesForModal = () => {
        const nm = nicknames.map((name, index) => {
            const li = document.createElement('li');
            li.classList.add('select-nickname');
            li.innerHTML = removeSVG;
            const span_ = document.createElement('span');
            span_.dataset.index = index;
            span_.innerText = `${name}`;
            li.prepend(span_);

            li.lastElementChild.addEventListener('click', () => {
                nicknames.splice(index, 1);
                li.remove();
                if (!nicknames.length) {
                    nicknamesHome.innerHTML = nonames
                }
            });
            return li;
        });

        nicknamesHome.innerHTML = '';

        if (nm.length) {
            nm.forEach((element) => nicknamesHome.appendChild(element));
        } else {
            nicknamesHome.innerHTML = nonames;
        }
    };

    const addNickname = (event_) => {
        if (event_.key === 'Enter') {
            event_.preventDefault();
            const newname = event_.target.value;

            if (newname) {
                const namesSplit = newname.split(',').map((name) => name.trim()).filter((name) => Boolean(name));
                nicknames.push(...namesSplit);
                createNicknamesForModal();
            };
        };
    };

    nicknamesModal.addEventListener('shown.bs.modal', () => {
        // add nicknames
        createNicknamesForModal();

        // enter new name
        nicknamesInput.addEventListener('keydown', addNickname);
    });

    nicknamesModal.addEventListener('hidden.bs.modal', () => {
        const savednicknameElements = nicknames.map((name) => {
            const li = document.createElement('li');
            li.innerHTML = name;
            return li;
        });
        savedNicknames.innerHTML = '';

        if (savednicknameElements.length) {
            savednicknameElements.forEach((nameElement) => savedNicknames.appendChild(nameElement));
        } else {
            savedNicknames.innerHTML = '<div class="alert alert-info">No nicknames</div>'
        }

        nicknamesformInput.value = nicknames.join(',') 
    });
}
