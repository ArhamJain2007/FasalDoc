import structlog
from app.config import settings

logger = structlog.get_logger()


class ModelLoader:
    _model = None
    _tflite = None
    _is_tflite: bool = False

    @classmethod
    async def load(cls) -> None:
        import tensorflow as tf

        # Try Keras model first
        try:
            cls._model = tf.keras.models.load_model(settings.MODEL_PATH)
            cls._is_tflite = False
            logger.info("Keras model loaded", path=settings.MODEL_PATH)
            return
        except Exception as keras_err:
            logger.warning("Keras model load failed", error=str(keras_err))

        # Try TFLite via tflite_runtime
        try:
            import tflite_runtime.interpreter as tflite
            cls._tflite = tflite.Interpreter(settings.TFLITE_MODEL_PATH)
            cls._tflite.allocate_tensors()
            cls._is_tflite = True
            logger.info("TFLite interpreter loaded", path=settings.TFLITE_MODEL_PATH)
            return
        except Exception:
            pass

        # Try TFLite via tf.lite
        try:
            import tensorflow as tf
            cls._tflite = tf.lite.Interpreter(settings.TFLITE_MODEL_PATH)
            cls._tflite.allocate_tensors()
            cls._is_tflite = True
            logger.info("TFLite loaded via tf.lite", path=settings.TFLITE_MODEL_PATH)
            return
        except Exception:
            pass

        # No model found — start without one, /detect returns 503
        logger.error(
            "No model file found. Place a model in the models/ folder. "
            "The /detect endpoint will return 503 until then."
        )

    @classmethod
    def get(cls):
        if cls._model is not None:
            return cls._model
        if cls._tflite is not None:
            return cls._tflite
        raise RuntimeError("Model not loaded.")

    @classmethod
    def is_tflite(cls) -> bool:
        return cls._is_tflite

    @classmethod
    def is_loaded(cls) -> bool:
        return cls._model is not None or cls._tflite is not None

    @classmethod
    def unload(cls) -> None:
        cls._model = None
        cls._tflite = None
        cls._is_tflite = False
        logger.info("ML model unloaded")