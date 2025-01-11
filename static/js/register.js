document.querySelector('.add-to-cart').addEventListener('click', function() {
    const category = document.getElementById("event-category").value;
    const dogName = document.getElementById("dog-name").value;
    const breed = document.getElementById("breed").value;
    const age = document.getElementById("age").value;

    // Ensure all fields are filled out
    if (dogName && breed && age) {
        const eventDetails = `${category} - ${dogName} (${breed}, Age: ${age})`;

        // Save event details to localStorage for My Events section
        let events = JSON.parse(localStorage.getItem("registeredEvents")) || [];
        events.push(eventDetails);
        localStorage.setItem("registeredEvents", JSON.stringify(events));

        // Get dog_id and competition_id from the button's data attributes
        const dogId = this.getAttribute('data-dog-id');
        const competitionId = this.getAttribute('data-competition-id');

        // Send data to backend (add to cart)
        fetch('/add_to_cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                dog_id: dogId,
                competition_id: competitionId,
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.message === 'Dog registered for the competition successfully') {
                alert("Registration Successful!\n" + eventDetails);
                window.location.href = "myevents.html"; // Redirect to My Events page
            } else {
                alert("Error: " + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error adding to cart.');
        });
    } else {
        alert("Please fill out all the details.");
    }
});
