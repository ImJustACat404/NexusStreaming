import yagmail

NEXUS_EMAIL = "nexus.streaming.system@gmail.com"
NEXUS_PASSWORD = input("Please enter email password: ")


def send_mail(recipient_email, subject, body):
    # Create a yagmail object
    yag = yagmail.SMTP(user=NEXUS_EMAIL, password=NEXUS_PASSWORD)
    # Send the email
    yag.send(to=recipient_email, subject=subject, contents=body)
    print(f"Email sent to {recipient_email}")


def send_verification_code(recipient_email, code):
    email_subject = "Welcome to Nexus!"
    email_body = f"Welcome to nexus streaming!\n\nYour verification code is: {code}"
    send_mail(recipient_email, email_subject, email_body)


def stream_summery(recipient_email, recipient_name, stream_name, max_views, likes, dislikes):
    email_subject = "Your Nexus live summary"
    email_body = (f"Thank you for using Nexus {recipient_name}!\n"
                  f"This is the summary of your stream \"{stream_name}\":\n\n"
                  f"You reached a maximum of {max_views} viewers! Amazing!\n"
                  f"{likes} people likes what you were doing!\n"
                  f"{dislikes} people think you can do better, don't take it too hard!\n\n"
                  f"Hope to see you again,\nThe Nexus team")
    send_mail(recipient_email, email_subject, email_body)
