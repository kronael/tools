# socksium

Chromium on a throwaway profile through a SOCKS5 proxy. The script deletes
the profile on exit. Chromium sends DNS through the proxy too.

```
ssh -D 1080 -N somehost &    # open the tunnel
socksium                     # browse through 127.0.0.1:1080
socksium 9050 example.com    # other port, open a url
```

`CHROMIUM=google-chrome socksium` uses another binary.

## Install

```
make install            # → ~/.local/bin/socksium
```
