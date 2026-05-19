import logging
import subprocess
import httpx
from app.services.llm import OLLAMA_MODEL

logger = logging.getLogger(__name__)

OLLAMA_HOST = "http://ollama:11434"


def ensure_model_available():
    """Check if the Ollama model is available via HTTP API."""
    for attempt in range(10):
        try:
            with httpx.Client(timeout=5) as client:
                resp = client.get(f"{OLLAMA_HOST}/api/tags")
                if resp.status_code == 200:
                    models = resp.json().get("models", [])
                    model_names = [m.get("name", "") for m in models]
                    if OLLAMA_MODEL in model_names:
                        logger.info(f"Ollama model '{OLLAMA_MODEL}' already available")
                        return
                    logger.info(f"Ollama running but model '{OLLAMA_MODEL}' not found")
                else:
                    raise RuntimeError(f"Ollama responded with {resp.status_code}")
        except httpx.ConnectError:
            logger.info(f"Ollama not ready yet, retrying ({attempt + 1}/10)...")
        except httpx.TimeoutException:
            logger.info(f"Ollama timeout, retrying ({attempt + 1}/10)...")
        except Exception as e:
            logger.warning(f"Ollama connection error: {e}")
            raise RuntimeError(f"Ollama connection error: {e}")
        import time
        time.sleep(3)
    raise RuntimeError("Ollama not reachable after 10 retries")
