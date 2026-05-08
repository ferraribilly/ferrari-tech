const mercadoPagoPublicKey = document.getElementById("mercado-pago-public-key")?.value;

if (!mercadoPagoPublicKey) throw new Error("PUBLIC KEY VAZIA");

const mercadopago = new MercadoPago(mercadoPagoPublicKey);



let cardPaymentBrickController;

async function loadPaymentForm() {
    const productCost = document.getElementById('amount')?.value || 0;

    const settings = {
        initialization: {
            amount: Number(productCost),
        },
        callbacks: {
            onReady: () => {
                console.log('brick ready');
            },
            onError: (error) => {
                alert(JSON.stringify(error));
            },
            onSubmit: (cardFormData) => {
                proccessPayment(cardFormData);
            }
        },
        locale: 'pt-BR',
        customization: {
            paymentMethods: {
                maxInstallments: 5
            },
            visual: {
                style: {
                    theme: 'dark',
                    customVariables: {
                        formBackgroundColor: '#1d2431',
                        baseColor: 'aquamarine'
                    }
                }
            }
        },
    };

    const bricks = mercadopago.bricks();

    cardPaymentBrickController = await bricks.create(
        'cardPayment',
        'mercadopago-bricks-contaner__PaymentCard',
        settings
    );
}



const proccessPayment = (cardFormData) => {


    // DEVICE ID (ANTIFRAUDE)
    // cardFormData.device_id = deviceId;

    fetch(`/process_payment/${usuario_id}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(cardFormData),
    })
    .then(response => response.json())
    .then(result => {
        // ✅ SEMPRE PREENCHE OS CAMPOS, MESMO QUE SEJA RECUSADO OU EM ANÁLISE
        document.getElementById("payment-id").innerText = result.id || "";
        document.getElementById("payment-status").innerText = result.status || "";
        document.getElementById("payment-detail").innerText = result.status_detail || "";

        $('.container__payment').fadeOut(500);

        setTimeout(() => {
            $('.container__result').show(500).fadeIn();
        }, 500);

        // Se tiver erro, mostra o alerta mas continua mostrando a tela
        if (result.error_message) {
            alert(JSON.stringify({
                status: result.status,
                message: result.error_message
            }));
        }
    })
    .catch(error => {
        alert("Unexpected error\n" + JSON.stringify(error));
    });
};


// transitions
document.getElementById('checkout-btn')?.addEventListener('click', function () {
    $('.container__cart').fadeOut(500);

    setTimeout(() => {
        updatePrice();
        loadPaymentForm();
        $('.container__payment').show(500).fadeIn();
    }, 500);
});

document.getElementById('go-back')?.addEventListener('click', function () {
    $('.container__payment').fadeOut(500);

    setTimeout(() => {
        $('.container__cart').show(500).fadeIn();
    }, 500);
});

// price
function updatePrice() {
    let total = 0;
    let totalQty = 0;

    const prices = document.querySelectorAll('.unit-price');
    const quantities = document.querySelectorAll('.quantity');

    prices.forEach((priceEl, index) => {
        const price = parseFloat(priceEl.innerText.replace(',', '.')) || 0;
        const qty = Number(quantities[index].value) || 1;

        total += price * qty;
        totalQty += qty;
    });

    document.getElementById('cart-total').innerText = 'R$ ' + total.toFixed(2);
    document.getElementById('summary-price').innerText = 'R$ ' + total.toFixed(2);
    document.getElementById('summary-quantity').innerText = totalQty;
    document.getElementById('summary-total').innerText = 'R$ ' + total.toFixed(2);
    document.getElementById('amount').value = total.toFixed(2);
}

// eventos
document.querySelectorAll('.quantity').forEach(input => {
    input.addEventListener('change', updatePrice);
});

updatePrice();
