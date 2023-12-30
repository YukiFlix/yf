var scrollBtn = document.getElementById("scrollBtn");

function scrollFunction() {
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
        window.scrollTo({ top: 0, behavior: "smooth" });
    }
}

scrollBtn.addEventListener("click", scrollFunction);

window.onscroll = function () {
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
        scrollBtn.style.display = "block";
    } else {
        scrollBtn.style.display = "none";
    }
};