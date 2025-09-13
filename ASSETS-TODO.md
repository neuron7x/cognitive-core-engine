# Assets TODO

This checklist tracks visual assets that need to be produced manually.

- [ ] `assets/og-banner.png` — 1280x640 social preview banner.
- [ ] `media/api-demo.gif` — 10–15s screencast showing API request/response.
- [ ] `media/cli-demo.gif` — 10–15s screencast of `cogctl` basic usage.
- [ ] Replace `assets/logo.svg` with final logo design if available.
- [ ] Replace `OWNER/REPO` placeholders in README badges with the actual repository slug.

## Capture commands

```bash
# Example using ffmpeg to record terminal
ffmpeg -f x11grab -video_size 1280x720 -i "$DISPLAY" -t 15 media/cli-demo.gif
```
