import React, { useState, useCallback, useMemo, useRef, useEffect, useContext } from 'react';
import {
  useParticipantIds,
  useScreenShare,
  useLocalParticipant,
  useDailyEvent,
  DailyAudio,
} from '@daily-co/daily-react';

import './Call.css';
import Tile from '../Tile/Tile';
import UserMediaError from '../UserMediaError/UserMediaError';
import { LanguageContext } from '../../contexts/Language/LanguageContext';

export default function Call() {
  /* If a participant runs into a getUserMedia() error, we need to warn them. */
  const [getUserMediaError, setGetUserMediaError] = useState(false);
  const [lang] = useContext(LanguageContext);
  const audioRef = useRef(null);
  /* We can use the useDailyEvent() hook to listen for daily-js events. Here's a full list
   * of all events: https://docs.daily.co/reference/daily-js/events */
  useDailyEvent(
    'camera-error',
    useCallback(() => {
      setGetUserMediaError(true);
    }, []),
  );

  /* This is for displaying remote participants: this includes other humans, but also screen shares. */
  const { screens } = useScreenShare();
  const remoteParticipantIds = useParticipantIds({ filter: 'remote' });

  /* This is for displaying our self-view. */
  const localParticipant = useLocalParticipant();
  const isAlone = useMemo(
    () => remoteParticipantIds?.length < 1 || screens?.length < 1,
    [remoteParticipantIds, screens],
  );

  useEffect(() => {
    // console.log('audioref current: ', audioRef.current);
    if (audioRef.current) {
      const audioTags = audioRef.current.getAllAudio();
      audioTags.forEach((t) => {
        if (t.dataset.sessionId) {
          if (lang.remote[t.dataset.sessionId]) {
            // this is an audio tag for a remote participant
            const langData = lang.remote[t.dataset.sessionId];

            // if their spoken language isn't what I want to hear, turn them down
            if (langData.spoken !== lang.local.audio) {
              t.volume = 0.1;
            } else {
              t.volume = 1;
            }
          } else if (lang.translators[t.dataset.sessionId]) {
            // This is the audio tag for a translator
            const langData = lang.translators[t.dataset.sessionId];
            if (langData.out === lang.local.audio) {
              t.volume = 1;
            } else {
              t.volume = 0;
            }
          }
        }
      });
    }
  }, [remoteParticipantIds]);

  const renderCallScreen = () => (
    <>
      <div className="call">
        {/* Your self view */}
        {localParticipant && <Tile id={localParticipant.session_id} isLocal isAlone={isAlone} />}
        {/* Videos of remote participants and screen shares */}

        {remoteParticipantIds.map((id) => (
          <Tile key={id} id={id} />
        ))}
        {screens.map((screen) => (
          <Tile key={screen.screenId} id={screen.session_id} isScreenShare />
        ))}
      </div>
      <DailyAudio ref={audioRef} />
    </>
  );

  return getUserMediaError ? <UserMediaError /> : renderCallScreen();
}
