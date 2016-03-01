(function() {

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

})();
