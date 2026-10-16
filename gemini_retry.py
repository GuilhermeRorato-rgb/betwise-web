"""Limited retries before any response text is emitted. No prompts in logs."""
import logging
import random
import time

LOG = logging.getLogger(__name__)
TRANSIENT_CODES = {500, 502, 503, 504}


def retry_stream(factory, *, attempts=3, sleep=time.sleep, jitter=random.uniform):
    emitted = False
    for attempt in range(attempts):
        stream = None
        try:
            stream = factory()
            for text in stream:
                if text:
                    emitted = True
                    yield text
            return
        except Exception as error:
            try:
                code = int(getattr(error, 'code', 0))
            except (TypeError, ValueError):
                code = 0
            retry = code in TRANSIENT_CODES and not emitted and attempt + 1 < attempts
            LOG.warning('Gemini failure code=%s attempt=%s partial=%s retry=%s',
                        code, attempt + 1, emitted, retry)
            if not retry:
                raise
        finally:
            if stream is not None:
                close = getattr(stream, 'close', None)
                if close:
                    close()
        sleep(2 ** (attempt + 1) + jitter(0, 0.5))


def retry_call(operation):
    def once():
        yield operation()
    return next(retry_stream(once))
