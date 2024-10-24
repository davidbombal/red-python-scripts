import subprocess
import re

# Obtener todos los perfiles Wi-Fi
command_output = subprocess.run(["netsh", "wlan", "show", "profiles"], capture_output=True).stdout.decode('latin-1')
profile_names = (re.findall("All User Profile     : (.*)\r", command_output))
wifi_list = []

# Verificar si existen perfiles Wi-Fi
if len(profile_names) != 0:
    for name in profile_names:
        # Diccionario para almacenar información del perfil Wi-Fi
        wifi_profile = {}
        profile_info = subprocess.run(["netsh", "wlan", "show", "profile", name], capture_output=True).stdout.decode('latin-1')

        # Verificar si la clave de seguridad está presente o ausente
        if re.search("Security key           : Absent", profile_info):
            continue  # Si la clave está ausente, pasar al siguiente perfil
        else:
            # Obtener el nombre de la red (SSID)
            wifi_profile["ssid"] = name
            # Obtener la información del perfil incluyendo la contraseña
            profile_info_pass = subprocess.run(["netsh", "wlan", "show", "profile", name, "key=clear"], capture_output=True).stdout.decode('latin-1')
            password = re.search("Key Content            : (.*)\r", profile_info_pass)

            # Verificar si la contraseña está presente o no
            if password is None:
                wifi_profile["password"] = None
            else:
                wifi_profile["password"] = password[1]
            wifi_list.append(wifi_profile)  # Agregar el perfil a la lista

# Imprimir la lista de perfiles Wi-Fi con sus contraseñas (si están disponibles)
for x in range(len(wifi_list)):
    print(wifi_list[x]) 
