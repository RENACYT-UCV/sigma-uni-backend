import smtplib
import ssl
from email.message import EmailMessage

def enviar_codigo(destinatario, codigo):
    email_emisor = "TUCORREO@gmail.com"
    email_contraseña = "TUPASSWORDDEAPLICACION"  # no es tu clave normal, sigue leyendo abajo
    asunto = "Código de verificación - Recuperar contraseña Sigma"
    cuerpo = f"Tu código de verificación para cambiar la contraseña es: {codigo}"

    em = EmailMessage()
    em["From"] = email_emisor
    em["To"] = destinatario
    em["Subject"] = asunto
    em.set_content(cuerpo)

    contexto = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=contexto) as smtp:
        smtp.login(email_emisor, email_contraseña)
        smtp.sendmail(email_emisor, destinatario, em.as_string())
