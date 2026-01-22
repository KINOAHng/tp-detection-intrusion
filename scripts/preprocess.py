import pandas as pd
import ipaddress

# Charger les fichiers (adapte les chemins si besoin pour l'évaluateur)
df_logs = pd.read_csv('Network_logs.csv', low_memory=False)
df_geo = pd.read_csv('dbip-country-lite-2026-01.csv', 
                     header=None, names=['start_ip', 'end_ip', 'country_code'])

def ip_to_country(ip_str):
    try:
        ip = ipaddress.ip_address(ip_str)
        if ip.is_private:
            return 'Private'
        
        ip_int = int(ip)
        mask = (df_geo['start_ip'] <= ip_int) & (ip_int <= df_geo['end_ip'])
        matching = df_geo[mask]
        if not matching.empty:
            return matching.iloc[0]['country_code']
        return 'Unknown'
    except:
        return 'Invalid'

print("Mapping des IPs en cours...")
df_logs['src_country'] = df_logs['Source_IP'].apply(ip_to_country)
df_logs['dst_country'] = df_logs['Destination_IP'].apply(ip_to_country)

# Supprimer IPs originales
df_logs = df_logs.drop(['Source_IP', 'Destination_IP'], axis=1)

# Vérifier résultat
print(df_logs.head(10))

# Sauvegarder le fichier nettoyé
df_logs.to_csv('cleaned_network_logs.csv', index=False)
print("Fichier nettoyé sauvegardé !")
