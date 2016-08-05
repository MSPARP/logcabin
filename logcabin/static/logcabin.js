(function() {

    // AJAX forms
    if (window.fetch) {
        var standard_headers = new Headers();
        standard_headers.append("X-Requested-With", "XMLHttpRequest");
        for (var form of document.querySelectorAll(".ajax_form")) {
            form.addEventListener("submit", function(e) {
                e.preventDefault();
                e.stopPropagation();
                if (this.classList.contains("in_progress")) { return false; }
                this.classList.add("in_progress");
                var error_container = this.querySelector(".error");
                if (error_container) { error_container.textContent = ""; }
                var data = {};
                var form = this;
                fetch(this.action, {
                    method: this.method,
                    headers: standard_headers,
                    credentials: "include",
                    body: new FormData(this),
                }).then(function(response) {
                    form.classList.remove("in_progress");
                    return response.json();
                }).then(function(data) {
                    if (data.error && error_container) {
                        error_container.textContent = data.error;
                    } else if (data.go_to_url) {
                        location.href = data.go_to_url;
                    }
                }).catch(function(reason) {
                    form.classList.remove("in_progress");
                    if (error_container) {
                        error_container.textContent = "This request couldn't be completed. Please try again later.";
                    }
                });
            });
        }
    }

    // Chapter editing
    if (window.fetch && document.body.classList.contains("editable")) {
        for (var link of document.querySelectorAll(".edit_link")) {
            link.addEventListener("click", function(e) {
                e.preventDefault();
                e.stopPropagation();

                var link = this;

                if (link.parentNode.previousElementSibling.tagName == "TEXTAREA") {
                    link.parentNode.previousElementSibling.remove();
                    link.parentNode.previousElementSibling.style.display = "block";
                    return;
                }

                if (link.classList.contains("loading")) { return; }
                link.classList.add("loading");

                fetch(this.href + ".json", {
                    method: "GET",
                    headers: standard_headers,
                    credentials: "include",
                }).then(response => response.json()).then(function(data) { // TODO i have no idea about browser support for arrow functions
                    link.classList.remove("loading");
                    link.parentNode.previousElementSibling.style.display = "none";
                    var textarea = document.createElement("textarea");
                    textarea.name = link.parentNode.parentNode.id.replace("message_","edit_");
                    textarea.innerHTML = data.text;
                    link.parentNode.parentNode.insertBefore(textarea, link.parentNode);
                    textarea.style.height = textarea.scrollHeight + "px";
                    textarea.addEventListener("keyup", function() {
                        this.style.height = this.scrollHeight - 40 + "px";
                    });
                }); // TODO catch

            });
        }
    }

})();
