// Get all the filter sections
const priceSection = document.getElementById('fs_price_body');
const marcaSection = document.getElementById('fs_distance_body');
const categoriaSection = document.getElementById('fs_time_body');
const ratingSection = document.getElementById('fs_rating');

// Get all the filter buttons
const priceButtons = priceSection.querySelectorAll('button');
const distanceButtons = distanceSection.querySelectorAll('li');
const timeButtons = timeSection.querySelectorAll('li');
const ratingButtons = ratingSection.querySelectorAll('li');

// Attach click event listeners to the filter buttons
priceButtons.forEach(button => {
  button.addEventListener('click', () => {
    // Remove the "active" class from all buttons in this section
    priceButtons.forEach(btn => btn.classList.remove('active'));

    // Add the "active" class to the clicked button
    button.classList.add('active');
  });
});

distanceButtons.forEach(button => {
  button.addEventListener('click', () => {
    // Remove the "active" class from all buttons in this section
    distanceButtons.forEach(btn => btn.classList.remove('active'));

    // Add the "active" class to the clicked button
    button.classList.add('active');
  });
});

timeButtons.forEach(button => {
  button.addEventListener('click', () => {
    // Remove the "active" class from all buttons in this section
    timeButtons.forEach(btn => btn.classList.remove('active'));

    // Add the "active" class to the clicked button
    button.classList.add('active');
  });
});

ratingButtons.forEach(button => {
  button.addEventListener('click', () => {
    // Remove the "active" class from all buttons in this section
    ratingButtons.forEach(btn => btn.classList.remove('active'));

    // Add the "active" class to the clicked button
    button.classList.add('active');
  });
});
