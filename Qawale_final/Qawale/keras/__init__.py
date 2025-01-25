# __init__.py

# Exportiere QawaleNNet und QawaleNNetWrapper für externe Nutzung
from .QawaleNNet import QawaleNNet, QawaleNNet
from .NNet import model

# Importiere TensorFlow Keras, falls es für die Initialisierung notwendig ist
try:
    import tensorflow.keras
except ImportError as e:
    raise ImportError("Keras konnte nicht importiert werden. Stellen Sie sicher, dass TensorFlow korrekt installiert ist.") from e


def models():
    return None
