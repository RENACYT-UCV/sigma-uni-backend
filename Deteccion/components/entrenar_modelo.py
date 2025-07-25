import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.utils import to_categorical
from sklearn.preprocessing import LabelEncoder
import joblib

# Leer los datos
data = pd.read_csv("datos/datos_señas.csv", header=None)
X = data.iloc[:, 1:].values
y = data.iloc[:, 0].values

# Codificar etiquetas (de texto a número)
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)
y_categorical = to_categorical(y_encoded)

# Guardar el codificador
joblib.dump(label_encoder, 'label_encoder.pkl')

# Dividir en entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y_categorical, test_size=0.2, random_state=42)

# Crear modelo
model = Sequential([
    Dense(128, activation='relu', input_shape=(63,)),
    Dense(64, activation='relu'),
    Dense(10, activation='softmax')  # 10 clases: del 0 al 9
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Entrenar
model.fit(X_train, y_train, epochs=30, batch_size=16, validation_data=(X_test, y_test))

# Guardar modelo
model.save('modelo_senas.h5')
