let totalCursos = parseInt(document.getElementById('totalCursos').value || 1);

function preguntasVideoPorDefecto(input) {
    if (!input.files || input.files.length === 0) return;

    const archivo = input.files[0];
    const videoWrapper = input.closest(".videoWrapper");

    videoWrapper.querySelector(".preguntasVideo")?.remove();

    const preguntasContainer = document.createElement("div");
    preguntasContainer.classList.add("preguntasVideo");
    preguntasContainer.innerHTML = `
        <h5>Examen para: ${archivo.name}</h5>
        ${[0,1,2,3].map(i => `
            <div class="mb-2">
                <input type="radio" name="correcta-${Date.now()}" value="${i}">
                <input type="text" class="form-control" placeholder="Opción ${i+1}">
            </div>
        `).join('')}
    `;
    videoWrapper.appendChild(preguntasContainer);
}

document.getElementById("btnAgregarCurso").addEventListener("click", function() {
    const original = document.querySelector(".cursoModulo");
    const clone = original.cloneNode(true);

    clone.querySelectorAll("input").forEach(input => {
        if (input.type === "text") input.value = "";
        if (input.type === "file") input.value = "";
        if (input.type === "radio") input.checked = false;
    });

    clone.querySelector(".videosContainer").innerHTML = `
        <div class="videoWrapper mb-2">
            <input type="file" class="form-control" name="videoSet-${totalCursos}[]" onchange="preguntasVideoPorDefecto(this)">
        </div>
    `;

    clone.dataset.cursoIndex = totalCursos;
    clone.querySelector("h3").textContent = `Curso #${totalCursos + 1}`;
    clone.querySelector("input[type='text']").name = `nombreCurso-${totalCursos}`;
    clone.querySelector(".btnAgregarVideo").dataset.curso = totalCursos;

    totalCursos++;
    document.getElementById('totalCursos').value = totalCursos;

    document.getElementById("clasesFormset").appendChild(clone);
});

document.addEventListener("click", function(e) {
    if (e.target && e.target.classList.contains("btnAgregarVideo")) {
        const cursoModulo = e.target.closest(".cursoModulo");
        const videosContainer = cursoModulo.querySelector(".videosContainer");
        const cursoIndex = cursoModulo.dataset.cursoIndex;

        const videoWrapper = document.createElement("div");
        videoWrapper.classList.add("videoWrapper", "mb-2");
        videoWrapper.innerHTML = `
            <input type="file" class="form-control" name="videoSet-${cursoIndex}[]" onchange="preguntasVideoPorDefecto(this)">
        `;
        videosContainer.appendChild(videoWrapper);
    }
});
