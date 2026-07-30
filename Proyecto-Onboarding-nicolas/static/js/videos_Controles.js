const video = document.querySelector("video");
const btn = document.querySelector(".btnSiguiente");

btn.style.display = "none";

video.addEventListener("ended", () => {
    btn.style.display = "inline-block";
});