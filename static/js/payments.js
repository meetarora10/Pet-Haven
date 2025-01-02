document.addEventListener("DOMContentLoaded", () => {
    const paymentForm = document.getElementById("paymentForm");
    const upiDetails = document.getElementById("upiDetails");
    const netBankingDetails = document.getElementById("netBankingDetails");
    const confirmation = document.getElementById("confirmation");

    // Show or hide payment details based on selection
    paymentForm.addEventListener("change", (event) => {
        const selectedPayment = event.target.value;

        upiDetails.style.display = selectedPayment === "upi" ? "block" : "none";
        netBankingDetails.style.display = selectedPayment === "netbanking" ? "block" : "none";
    });

    // Handle form submission
    paymentForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        // Get the selected payment method
        const selectedPayment = document.querySelector('input[name="paymentMethod"]:checked');

        // First check if any payment method is selected
        if (!selectedPayment) {
            alert("Please select a payment method.");
            return;
        }

        let canProceed = false;
        const paymentMethod = selectedPayment.value;

        // Validate based on selected payment method
        switch(paymentMethod) {
            case "netbanking":
                const bank = document.getElementById("bank").value;
                if (!bank || bank === "--Select a Bank--") {
                    alert("Please select a bank for Net Banking.");
                } else {
                    canProceed = true;
                }
                break;

            case "upi":
                const upiId = document.getElementById("upiId").value;
                if (!upiId) {
                    alert("Please enter your UPI ID.");
                } else if (!/^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+$/.test(upiId)) {
                    alert("Please enter a valid UPI ID (e.g., username@bank)");
                } else {
                    canProceed = true;
                }
                break;

            default:
                alert("Please select a valid payment method.");
                return;
        }

        // Only proceed if validation passed
        if (canProceed) {
            try {
                const response = await fetch('/complete_payment', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        paymentMethod: paymentMethod,
                        upiId: paymentMethod === "upi" ? document.getElementById("upiId").value : null,
                        bank: paymentMethod === "netbanking" ? document.getElementById("bank").value : null
                    })
                });

                if (response.ok) {
                    alert("Payment Successful!");
                    window.location.href = "/";
                } else {
                    throw new Error('Payment failed');
                }
            } catch (error) {
                alert("Payment failed. Please try again.");
                console.error('Error:', error);
            }
        }
    });
});