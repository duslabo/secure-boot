# SDLS study guide: source

Interactive course on CCSDS 355.0-B-2 (Space Data Link Security Protocol). `build.py` generates the page from `learn.css`, `learn.js` and the diagram helpers in `svgkit.py`.

```sh
python3 build.py /tmp/body.html ../sdls-study-guide.html
```

Open `../sdls-study-guide.html` in a browser. Progress and mastery scores are kept in the browser's localStorage.
