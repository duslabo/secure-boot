# TC4xx secure boot deck: source

`build.py` generates the slide deck from `deck.css` and `deck.js`. Diagrams are inline SVG laid out on a 4px grid.

```sh
python3 build.py /tmp/deck-body.html ../tc4xx-secure-boot-deck.html
```

The first argument is the body-only variant used for publishing as an artifact; the second is the standalone page.

Open `../tc4xx-secure-boot-deck.html` in a browser. Arrow keys or Space to navigate, `N` toggles speaker notes. Below 820px wide the slides stack as cards.
