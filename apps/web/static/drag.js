document.addEventListener("DOMContentLoaded", function () {
    const uploadContainer = document.getElementById('upload-container'),
          fileInput       = document.getElementById('file-input'),
          uploadButton     = document.getElementById('upload-button');

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Drag and drop upload
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadContainer.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadContainer.addEventListener(eventName, () => uploadContainer.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadContainer.addEventListener(eventName, () => uploadContainer.classList.remove('dragover'), false);
    });

    uploadContainer.addEventListener('drop', handleDrop, false);
    fileInput.addEventListener('change', handleFiles);

    function handleFiles(e) {
        uploadButton.style.display = 'inline-block';
        const files = e.target.files || e.dataTransfer.files;
        if (files.length > 0) {
            const fileName = files[0].name;
        }
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        fileInput.files = files; 
        handleFiles(e);
    }
});


const drag = document.getElementsByClassName("draggable");
for (let i = 0; i < drag.length; ++i) {
    dragElement(drag[i]);
}

let firstDrag = true;
function dragElement(element) {
    let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;

    element.onmousedown = dragMouseDown;

    function dragMouseDown(e) {
        // LET ME TYPE 
        let isFormElement = ['INPUT', 'BUTTON'].includes(e.target.nodeName);
        if (isFormElement) return;

        e.preventDefault();

        if (firstDrag) {
            // keep original grid positions, prevent grid from immediately collapsing on itself
            for (let i = 0; i < drag.length; ++i) {
                let pos = drag[i].getBoundingClientRect();
                setTimeout(() => { drag[i].style.position = "absolute"; }, 1);
                drag[i].style.top = pos.top + "px";
                drag[i].style.left = pos.left + "px";
            }
            firstDrag = false;
        }

        pos3 = e.clientX;
        pos4 = e.clientY;
        document.onmouseup = closeDragElement;
        document.onmousemove = elementDrag;
    }

    function elementDrag(e) {
        e.preventDefault();

        let pos = element.getBoundingClientRect();
        pos1 = pos3 - e.clientX;
        pos2 = pos4 - e.clientY;
        pos3 = e.clientX;
        pos4 = e.clientY;
        element.style.top = (pos.top - pos2) + "px";
        element.style.left = (pos.left - pos1) + "px";
    }

    function closeDragElement() {
        document.onmouseup = null;
        document.onmousemove = null;
    }
}