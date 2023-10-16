from twilio.rest import Client

account_sid = 'AC11621a0cb562b87c9f91956fdfb70b94'
auth_token = '4a9fccb7edd39e7b9a87e5bfb94cb80e'
client = Client(account_sid, auth_token)

message = client.messages.create(
  from_='whatsapp:+14155238886',
  body='Your appointment is coming up on July 21 at 3PM',
  to='whatsapp:+15183149542'
)

print(message.sid)