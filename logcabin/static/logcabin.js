(function() {

    if (window.fetch) {
        var standard_headers = new Headers();
        standard_headers.append("X-Requested-With", "XMLHttpRequest");
        for (var form of document.querySelectorAll(".ajax_form")) {
            form.addEventListener("submit", function(e) {
                /* TODO don't allow re-submitting until complete */
                /* TODO handle network errors */
                var error_container = this.querySelector(".error");
                if (error_container) { error_container.textContent = ""; }
                var data = {};
                fetch(this.action, {
                    method: this.method,
                    headers: standard_headers,
                    credentials: "include",
                    body: new FormData(this),
                }).then(function(response) {
                    return response.json();
                }).then(function(data) {
                    if (data.error && error_container) {
                        error_container.textContent = data.error;
                    } else if (data.go_to_url) {
                        location.href = data.go_to_url;
                    }
                });
                e.preventDefault();
                e.stopPropagation();
            });
        }
    }

})();
