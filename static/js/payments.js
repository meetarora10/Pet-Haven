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
    function validateCardDetails(cardType) {
        const prefix = cardType === "creditCard" ? "" : "debit";
        const cardNumber = document.getElementById(`${prefix}CardNumber`).value.replace(/\s/g, '');
        const expiryDate = document.getElementById(`${prefix}ExpiryDate`).value;
        const cvv = document.getElementById(`${prefix}Cvv`).value;
        const cardName = document.getElementById(`${prefix}CardName`).value;

        // Card number validation (16 digits)
        if (!/^\d{16}$/.test(cardNumber)) {
            alert("Please enter a valid 16-digit card number.");
            return false;
        }

        // Expiry date validation (MM/YY format)
        if (!/^(0[1-9]|1[0-2])\/([0-9]{2})$/.test(expiryDate)) {
            alert("Please enter a valid expiry date (MM/YY).");
            return false;
        }

        // Check if card is expired
        const [month, year] = expiryDate.split('/');
        const currentDate = new Date();
        const cardDate = new Date(2000 + parseInt(year), parseInt(month) - 1);
        if (cardDate < currentDate) {
            // alert("Card has expired.");
            return false;
        }

        // CVV validation (3 digits)
        if (!/^\d{3}$/.test(cvv)) {
            // alert("Please enter a valid 3-digit CVV.");
            return false;
        }

        // Name validation (at least 3 characters, letters and spaces only)
        if (!/^[a-zA-Z\s]{3,}$/.test(cardName)) {
            // alert("Please enter a valid name on card (minimum 3 characters).");
            return false;
        }

        return true;
    }
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
            case "creditCard":
                canProceed = validateCardDetails("creditCard");
                break;
    
            case "debitCard":
                canProceed = validateCardDetails("debitCard");
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
                        bank: paymentMethod === "netbanking" ? document.getElementById("bank").value : null,
                        cardNumber: paymentMethod === "creditcard" ? document.getElementById("cardNumber").value : null,
                        cardExpiry: paymentMethod === "creditcard" ? document.getElementById("expiryDate").value : null,
                        cardCVC: paymentMethod === "creditcard" ? document.getElementById("cvv").value : null,
                        cardName: paymentMethod === "creditcard" ? document.getElementById("cardName").value : null,
                        debitCardNumber: paymentMethod === "debitcard" ? document.getElementById("debitCardNumber").value : null,
                        debitCardExpiry: paymentMethod === "debitcard" ? document.getElementById("debitExpiryDate").value : null,
                        debitCardCVC: paymentMethod === "debitcard" ? document.getElementById("debitCvv").value : null,
                        debitCardName: paymentMethod === "debitcard" ? document.getElementById("debitCardName").value : null,
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