<h1 align="center">
  Skippex<br>
  <img src="https://img.shields.io/pypi/v/skippex">
  <img src="https://img.shields.io/pypi/status/skippex">
  <img src="https://img.shields.io/badge/plex%20web%20app-supported-success">
  <img src="https://img.shields.io/badge/chromecast-supported-success">
  <img src="https://img.shields.io/badge/plex%20for%20iOS-supported-success">
  <img src="https://img.shields.io/badge/remote%20users-unsupported-critical">
</h1>

<p align="center">
  <em>Skippex automatically skips intros for you on Plex, with support for the
  Chromecast.</em>
</p>

**IMPORTANT NOTE**: This is still pretty much beta software. Expect bugs and
please report them!

## Installation

Installing through **Docker** is the easiest way to get started:

```console
$ docker pull ghcr.io/svaikstude/skippex
```

*Docker-compose example coming soon.*

If you prefer not to use Docker, you can also use [**pipx**][pipx], which will
install Skippex in its own virtual environment:

```console
$ pipx install skippex
```

Or you can just use **pip**:

```console
$ pip install --user skippex
```

[pipx]: https://pipxproject.github.io/pipx/

## Usage

The first time you use Skippex, you'll first have to authorize the application
with Plex using the following command. This will open a new tab in your Web
browser allowing you to authenticate and authorize the application to access
your Plex account.

<table>
  <tr>
    <th>Docker</th>
    <th>pipx & pip</th>
  </tr>
  <tr>
    <td>
      <code>$ docker run -v skippex:/data --network host ghcr.io/svaikstude/skippex auth</code>
    </td>
    <td>
      <code>$ skippex auth</code>
    </td>
  </tr>
</table>

Once that's done, you can simply run Skippex and it'll start monitoring your
playback sessions and automatically skip intros for you on supported devices:

<table>
  <tr>
    <th>Docker</th>
    <th>pipx & pip</th>
  </tr>
  <tr>
    <td>
      <code>$ docker run -v skippex:/data --network host ghcr.io/svaikstude/skippex run</code>
    </td>
    <td>
      <code>$ skippex run</code>
    </td>
  </tr>
</table>

Et voilà! When this command says "Ready", Skippex is monitoring your shows and
will automatically skip intros for you.

*Note: Due to a [Chromecast limitation][cast-diff-subnets], the Docker container
has to run with host mode networking.*

[cast-diff-subnets]: https://www.home-assistant.io/integrations/cast#docker-and-cast-devices-and-home-assistant-on-different-subnets

## Things to know

 * **Clients need to have "Advertise as player" enabled.**
 * Only works for players on the local network.
 * Only skips once per playback session.
 * Solely based on the intro markers detected by Plex; Skippex does not attempt
   to detect intros itself.

## Tested and supported players

 * Plex Web App
 * Plex for iOS (both iPhone and iPad)
 * Chromecast v3

The NVIDIA SHIELD might be supported as well, but I don't have one so I can't
test it. Other players might also be supported. In any case, please inform me
by [creating a new issue][new_issue], so I can add your player to this list.

[new_issue]: https://github.com/svaikstude/skippex/issues/new

## Known issues

 * With a Chromecast, when seeking to a position, the WebSocket only receives
   the notification 10 seconds later. Likewise, the HTTP API starts returning
   the correct position only after 10 seconds. This means that if, before the
   intro, the user seeks to within 10 seconds of the intro, they may view it for
   a few seconds (before the notification comes in and saves us).

   One workaround would be to listen to Chromecast status updates using
   `pychromecast`, but that would necessitate a rearchitecture of the code.
