# GemFinder
I got mad at Spotify for not allowing me to rank tracks by stream counts inside album views.

# Installation
- `pip install -r requirements.txt`
- rename `.env.example` to `.env`
- grab `AUTH_TOKEN` from a valid Spotify session
- grab `CLIENT_TOKEN`from a valid Spotify Desktop installation (this one might be tricky, as you need to intercept their SSL traffic. Install a root CA onto `/usr/local/share/ca-certificates`, run `update-ca-certificates` and sniff away)
- `AUTH_TOKEN` has a small lifespan so you might need to renew it from time to time or else app will break when trying to rip a JSON and finding a fat 401 in its face
- enjoy

# Usage
`flask run`

# Preview
![Screenshot of GemFinder](screenshot.png "_Amazing_ css skillz")