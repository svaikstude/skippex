import logging
from dataclasses import replace
from typing import Optional, Set, Tuple, cast

from .seekables import Seekable, SeekableNotFoundError, SeekableProvider
from .sessions import EpisodeSession, Session, SessionExtrapolator, SessionListener

logger = logging.getLogger(__name__)


class AutoSkipper(SessionListener, SessionExtrapolator):
    def __init__(self, seekable_provider: SeekableProvider):
        self._sp = seekable_provider
        self._skipped_intro: Set[Session] = set()
        self._skipped_credits: Set[Session] = set()

    def trigger_extrapolation(self, session: Session, listener_accepted: bool) -> bool:
        # Note it's only useful to do this when the state is 'playing':
        #  - When it's 'paused', we'll receive another notification either as
        #    soon as the state changes, or every 10 second while it's paused.
        #  - When it's 'buffering', we'll also receive another notification as
        #    soon as the state changes. And I assume we'd also get notified
        #    every 10 second otherwise.
        #  - When it's 'stopped', we've already sent a signal to the dispatcher.

        if not listener_accepted:
            logger.debug("No extrapolation: listener rejected")
            return False

        session = cast(EpisodeSession, session)  # Safe because listener_accepted.

        # The listener accepted the session, and it may have skipped the intro.
        # In that case, we don't wanna extrapolate the session.
        return session

    def extrapolate(self, session: Session) -> Tuple[Session, int]:
        session = cast(EpisodeSession, session)  # Safe thanks to trigger_extrapolation().
        delay_ms = 1000
        new_view_offset_ms = session.view_offset_ms + delay_ms
        return replace(session, view_offset_ms=new_view_offset_ms), delay_ms

    def accept_session(self, session: Session) -> bool:
        if not isinstance(session, EpisodeSession):
            # Only TV shows have intro markers, other media don't interest us.
            logger.debug("Ignored; not an episode")
            return False

        if session.state != "playing":
            logger.debug(f'Ignored; state is "{session.state}" instead of "playing"')
            return False

        return True

    def on_session_activity(self, session: Session):
        session = cast(EpisodeSession, session)  # Safe thanks to accept_session().
        logger.debug(f"session_activity: {session}")

        intro_marker = session.intro_marker()
        pre_credits_scene_marker = session.pre_credits_scene_marker()
        ending_marker = session.ending_marker()
        view_offset_ms = session.view_offset_ms

        logger.debug(f"session.key={session.key}")
        logger.debug(f"session.view_offset_ms={session.view_offset_ms}")
        logger.debug(f"intro_marker={intro_marker}")
        logger.debug(f"pre_credits_scene_marker={pre_credits_scene_marker}")
        logger.debug(f"ending_marker={ending_marker}")

        if intro_marker.start <= view_offset_ms < intro_marker.end:
            seekable = self._get_seekable(session=session)
            if seekable:
                if session not in self._skipped_intro:
                    seekable.seek(intro_marker.end)
                    self._skipped_intro.add(session)
                    logger.info(
                        f"Session {session.key}: skipped intro (seeked from {view_offset_ms} to {intro_marker.end})"  # noqa: E501
                    )
        if pre_credits_scene_marker.start <= view_offset_ms < pre_credits_scene_marker.end:
            seekable = self._get_seekable(session=session)
            if seekable:
                if session not in self._skipped_credits:
                    seekable.seek(pre_credits_scene_marker.end)
                    self._skipped_credits.add(session)
                    logger.info(
                        f"Session {session.key}: skipped credits (seeked from {view_offset_ms} to {intro_marker.end})"  # noqa: E501
                    )
        if view_offset_ms >= ending_marker:
            seekable = self._get_seekable(session=session)
            if seekable:
                seekable.skip_next()
                logger.info(f"Session {session.key}: skipped to next item")

        logger.debug("-----")

    def _get_seekable(self, session: Session) -> Optional[Seekable]:
        try:
            return self._sp.provide_seekable(session)
        except SeekableNotFoundError as e:
            if e.has_plex_player_not_found():
                logger.error(
                    'Plex player not found for session; ensure "advertise ' 'as player" is enabled'
                )
            logger.exception(f"Cannot skip to next item for session {session.key}")
            return None

    def on_session_removal(self, session: Session):
        self._skipped_intro.discard(session)
        self._skipped_credits.discard(session)
