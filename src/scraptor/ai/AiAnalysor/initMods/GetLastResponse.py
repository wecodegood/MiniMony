def GetLastResponse(
    page,
    max_wait_ms: int = 10000000,
    stable_checks_required: int = 5,
    poll_interval_s: float = 0.2,
    min_start_chars: int = 5,
    on_update=None,
    strip_prefix: str | None = None,
):
    import time


    # Wait for any message container to appear (initial 10s)
    page.wait_for_selector(".ds-message", timeout=100000)

    last_text = ""
    stable_count = 0
    started = False

    deadline = time.monotonic() + (max_wait_ms)

    while True:
        try:
            # Prefer CSS selector; it is faster and simpler
            messages = page.locator(".ds-message").all()

            if messages:
                current_text = messages[-1].text_content() or ""

                if strip_prefix and current_text.startswith(strip_prefix):
                    current_text = current_text[len(strip_prefix):]

                # Mark as started when we have a minimal amount of content
                if not started and len(current_text) >= min_start_chars:
                    started = True

                if started:
                    if current_text == last_text:
                        stable_count += 1
                        if stable_count >= stable_checks_required:
                            return current_text
                    else:
                        stable_count = 0
                        last_text = current_text
                        if on_update:
                            try:
                                on_update(current_text)
                            except Exception:
                                # Do not break the loop if a user-supplied callback fails
                                pass
        except Exception:
            # Ignore transient DOM/read errors while polling
            pass

        if time.monotonic() >= deadline:
            # Timeout: return the latest text we have (possibly empty)
            return last_text

        time.sleep(poll_interval_s)
