function submitFavoriteForm(sneakerId) {
    var form = document.getElementById('add-favorite-form-' + sneakerId);
    form.submit();
}
function submitRemoveFavoriteForm(sneakerId) {
    var form = document.getElementById('remove-favorite-form-' + sneakerId);
    form.submit();
}