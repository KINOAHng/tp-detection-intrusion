import pandas as pd
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib

# Charger le fichier nettoyé
df = pd.read_csv('cleaned_network_logs.csv')

# Label et features
y = df['Intrusion']
X = df.drop('Intrusion', axis=1)

categorical_cols = ['Request_Type', 'Protocol', 'User_Agent', 'Status', 'Scan_Type', 'src_country', 'dst_country']
numerical_cols = ['Port', 'Payload_Size']

# Préprocesseur
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_cols),
        ('num', StandardScaler(), numerical_cols)
    ])

X_processed = preprocessor.fit_transform(X)

# Split train/test
X_train, X_test, y_train, y_test = train_test_split(X_processed, y, test_size=0.2, random_state=42, stratify=y)

# Modèle
model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
model.fit(X_train, y_train)

# Prédictions
y_pred = model.predict(X_test)

# Résultats
print("Accuracy :", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred, target_names=['Normal', 'Intrusion']))

# Sauvegarder
joblib.dump(preprocessor, 'preprocessor.joblib')
joblib.dump(model, 'random_forest_model.joblib')
print("Modèle et preprocessor sauvegardés !")
