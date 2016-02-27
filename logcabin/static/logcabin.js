(function() {

    if (window.fetch) {
        for (var form of document.querySelectorAll(".ajax_form")) {
            form.addEventListener("submit", function(e) {
                fetch(this.action).then(function() {
                    console.log("aaaaaaaaaa");
                });
                e.preventDefault();
                e.stopPropagation();
            });
        }
    }

})();
