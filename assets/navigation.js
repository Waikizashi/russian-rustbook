/* Native keyboard activation for the accessible mdBook sidebar button.
 * Run after mdBook's click listeners have observed the original checkbox state.
 */
(function () {
    const button = document.getElementById('mdbook-sidebar-toggle');
    const checkbox = document.getElementById('mdbook-sidebar-toggle-anchor');
    if (button && checkbox) {
        button.addEventListener('click', function () {
            queueMicrotask(function () {
                checkbox.checked = !checkbox.checked;
                checkbox.dispatchEvent(new Event('change'));
            });
        });
    }
})();
