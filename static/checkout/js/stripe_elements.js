var stripe_public_key = $('#id_stripe_public_key').text().slice(1,-1);
var stripe_client_secret = $('#id_stripe_client_secret').text().slice(1,-1);
var stripe = Stripe(stripe_public_key);
var elements = stripe.elements();
var card = elements.create('card', { style: style });

var style = {
  base: {
    color: '#32325d',
    fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
    fontSmoothing: 'antialiased',
    fontSize: '16px',
    '::placeholder': {
      color: '#aab7c4'
    }
  },
  invalid: {
    color: '#fa755a',
    iconColor: '#fa755a'
  }
};

card.mount('#card-element');
