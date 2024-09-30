onUiLoaded(() => {

    ['txt', 'img'].forEach((mode) => {
        const container = document.getElementById(`flux-colorwheel-${mode}`);
        container.style.height = '320px';
        container.style.width = '320px';
        container.style.margin = 'auto';

        const wheel = container.querySelector('img');
        container.insertBefore(wheel, container.firstChild);

        while (container.firstChild !== container.lastChild)
            container.lastChild.remove();

        wheel.ondragstart = (e) => { e.preventDefault(); return false; };
        wheel.id = `flux-img-${mode}`;
    });

});
