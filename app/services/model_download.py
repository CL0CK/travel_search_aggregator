import logging
import subprocess
from app.services.llm import OLLAMA_MODEL

logger = logging.getLogger(__name__)


def ensure_model_available():
    """Pull the Ollama model if not already present."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if OLLAMA_MODEL in result.stdout:
            logger.info(f"Ollama model '{OLLAMA_MODEL}' already available")
            return
        logger.info(f"Pulling Ollama model '{OLLAMA_MODEL}'...")
        subprocess.run(
            ["ollama", "pull", OLLAMA_MODEL],
            check=True,
            timeout=600,
        )
        logger.info(f"Model '{OLLAMA_MODEL}' pulled successfully")
    except FileNotFoundError:
        logger.warning(
            "Ollama not found. Install from https://ollama.ai and run 'ollama pull qwen3.5:4b'"
        )
        raise RuntimeError("Ollama is not installed")
    except subprocess.TimeoutExpired:
        logger.warning("Ollama pull timed out")
        raise RuntimeError("Ollama model pull timed out")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to pull model: {e}")
        raise RuntimeError(f"Failed to pull Ollama model: {e}")
