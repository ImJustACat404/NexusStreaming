import yagmail

NEXUS_EMAIL = "nexus.streaming.system@gmail.com"
NEXUS_PASSWORD = input("Please enter email password: ")


def send_mail(recipient_email, subject, body):
    """
    A function that emails a client
    :param recipient_email: The client's email address
    :type recipient_email: str
    :param subject: The email's subject
    :type subject: str
    :param body: The body of the email
    :type body: str
    """
    try:
        # Create a yagmail object
        yag = yagmail.SMTP(user=NEXUS_EMAIL, password=NEXUS_PASSWORD)
        # Send the email
        yag.send(to=recipient_email, subject=subject, contents=body)
        print(f"Email sent to {recipient_email}")
    except Exception as error:
        print(f"Could not send mail to {recipient_email}! Error: {error}")


def send_verification_code(recipient_email, code):
    """
    A function that email a verification code to a client
    :param recipient_email: The client's email adress
    :type recipient_email: str
    :param code: The verification code
    :type code: str
    """
    email_subject = "Welcome to Nexus!"
    email_body = f"Welcome to nexus streaming!\n\nYour verification code is: {code}"
    send_mail(recipient_email, email_subject, email_body)


def stream_summery(recipient_email, recipient_name, stream_name, max_views, likes, dislikes):
    """
    A function that emails a summary to a client after a stream
    :param recipient_email: The client's email address
    :type recipient_email: str
    :param recipient_name: The client's name
    :type recipient_name: str
    :param stream_name: The stream's title
    :type stream_name: str
    :param max_views: The maximus number of watchers in the client's stream
    :type max_views: int
    :param likes: The number of likes the stream got
    :type likes: int
    :param dislikes: The number of dislikes the video got
    :type dislikes: int
    """
    email_subject = "Your Nexus live summary"
    email_body = (f"Thank you for using Nexus {recipient_name}!\n"
                  f"This is the summary of your stream \"{stream_name}\":\n\n"
                  f"You reached a maximum of {max_views} viewers! Amazing!\n"
                  f"{likes} people liked what you were doing!\n"
                  f"{dislikes} people think you can do better, don't take it too hard!\n\n"
                  f"Hope to see you again,\nThe Nexus team")
    send_mail(recipient_email, email_subject, email_body)
