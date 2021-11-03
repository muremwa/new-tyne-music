

/* Preview images and refuse aspect ratio */
const hiddingClass = 'visually-hidden';
const invalidClass = 'is-invalid';

[...document.getElementsByClassName('js-img-pr')].forEach((element) => {
    const image = element.firstElementChild;

    if (image) {
        const aspectRatio = image.dataset.aspectRatio.split(':').map((int) => parseInt(int));
        const inputName = image.dataset.inputName;

        if (inputName && aspectRatio) {
            const alertDiv = document.getElementById(`alert-${inputName}`);
            const imageInput = document.getElementById(`id_${inputName}`);

            if (imageInput) {
                imageInput.addEventListener('change', (event_) => {
                    const reader = new FileReader();
                    const pimage = new Image();

                    pimage.onload = (imageEvent) => {
                        const height = imageEvent.target.height;
                        const width = imageEvent.target.width;
                        
                        if (width && height) {
                            if (((width / height) * aspectRatio[1]) === aspectRatio[0]) {
                                alertDiv.classList.add(hiddingClass);
                                imageInput.classList.remove(invalidClass);
                                imageInput.setCustomValidity('');
                            } else {
                                alertDiv.classList.remove(hiddingClass);
                                imageInput.classList.add(invalidClass);
                                imageInput.setCustomValidity(`The dimensions of '${inputName}' are not ${aspectRatio[0]} × ${aspectRatio[1]}`);
                            };
                        };                        
                    };

                    reader.onload = (readerEvent) => {
                        const newImage = readerEvent.target.result;
                        image.src = newImage;
                        pimage.src = newImage;
                    };
                    reader.readAsDataURL(event_.target.files[0])
                });
            };
        };
    };
});



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
                };
            });
            return li;
        });

        nicknamesHome.innerHTML = '';

        if (nm.length) {
            nm.forEach((element) => nicknamesHome.appendChild(element));
        } else {
            nicknamesHome.innerHTML = nonames;
        };
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
        };

        nicknamesformInput.value = nicknames.join(',') 
    });
};
