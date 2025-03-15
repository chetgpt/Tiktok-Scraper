async def attach_event_listeners(page):
    """
    Attaches event listeners to the page to record:
    - Throttled mousemove events (every 100ms).
    - Click events, capturing details about the clicked button.
    Listeners are stored on the window object for later removal.
    """
    await page.evaluate("""
        (() => {
            // Initialize recordedEvents array if not present
            if (!window.recordedEvents) {
                window.recordedEvents = [];
            }
            // Attach mousemove listener if not already attached
            if (!window.mousemoveListener) {
                function throttle(callback, delay) {
                    let last;
                    return function() {
                        const now = Date.now();
                        if (!last || now - last >= delay) {
                            last = now;
                            callback.apply(this, arguments);
                        }
                    }
                }
                window.mousemoveListener = throttle(function(e) {
                    window.recordedEvents.push({
                        event: 'mousemove',
                        x: e.clientX,
                        y: e.clientY,
                        timestamp: Date.now()
                    });
                }, 100);
                document.addEventListener('mousemove', window.mousemoveListener);
            }
            // Attach click listener if not already attached
            if (!window.clickListener) {
                window.clickListener = function(e) {
                    let path = e.composedPath();
                    let targetElem = e.target;
                    // Find the first button in the composed path
                    for (let el of path) {
                        if (el.tagName && el.tagName.toLowerCase() === 'button') {
                            targetElem = el;
                            break;
                        }
                    }
                    // Build DOM path
                    let domPath = [];
                    let el = targetElem;
                    while (el) {
                        if (el.tagName) {
                            domPath.unshift(el.tagName);
                        }
                        el = el.parentElement;
                    }
                    // Function to generate a robust selector
                    function getRobustSelector(el) {
                        if (!el) return "";
                        if (el.id) return "#" + el.id;
                        let selector = el.tagName.toLowerCase();
                        if (el.classList.length > 0) {
                            selector += "." + Array.from(el.classList).join(".");
                        }
                        return selector;
                    }
                    let robustSelector = getRobustSelector(targetElem);
                    window.recordedEvents.push({
                        event: 'click',
                        targetHTML: targetElem.outerHTML,
                        domPath: domPath.join(" > "),
                        robustSelector: robustSelector,
                        timestamp: Date.now()
                    });
                };
                document.addEventListener('click', window.clickListener, true);
            }
        })();
    """)
    print("[INFO] Event listeners attached.")
