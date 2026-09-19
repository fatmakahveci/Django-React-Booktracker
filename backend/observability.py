"""Strip sensitive request context before optional error reports leave the service."""


def scrub_event(event, hint):
    event.pop("user", None)
    event.pop("breadcrumbs", None)
    event.pop("extra", None)
    event.pop("logentry", None)
    request = event.get("request", {})
    event["request"] = {"method": request.get("method")}
    # Stack locals can contain credentials or book notes.
    for value in event.get("exception", {}).get("values", []):
        value["value"] = "Exception message redacted."
        for frame in value.get("stacktrace", {}).get("frames", []):
            frame.pop("vars", None)
    return event
