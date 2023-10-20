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
  const audioRef = useRef(null);
  const [lang, setLang] = useContext(LanguageContext);

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

  const botID = useParticipantIds({
    filter: (f) => f.user_name === 'Translatorbot',
  });

  useEffect(() => {
    console.log('audioref current: ', audioRef.current);
    console.log('botID: ', botID);
    if (audioRef.current && botID.length > 0) {
      // Need to wait for the session id attr to exist on the
      // audio node
      setTimeout(() => {
        let botVolume = 0.0;
        let allVolume = 1.0;
        if (lang.audio === 'french') {
          botVolume = 1.0;
          allVolume = 0.1;
        }
        console.log('bot id 0', botID[0]);
        const allAudio = audioRef.current.getAllAudio();
        const botAudio = audioRef.current.getAudioBySessionId(botID[0]);
        console.log({ allAudio, botAudio });
        // Turn everybody down, then turn the bot back up

        allAudio.forEach((a) => {
          console.log('setting ', a, ' to volume ', allVolume);
          a.volume = allVolume;
          console.log('volume is now ', a.volume);
        });
        console.log('setting bot to volume ', botVolume);

        botAudio.volume = botVolume;
        console.log('bot volume is now ', botAudio.volume);
      }, 1000);
    }
  }, [remoteParticipantIds]);

  const renderCallScreen = () => (
    <div className={screens.length > 0 ? 'is-screenshare' : 'call'}>
      {/* Your self view */}
      {localParticipant && <Tile id={localParticipant.session_id} isLocal isAlone={isAlone} />}
      {/* Videos of remote participants and screen shares */}
      {remoteParticipantIds?.length > 0 || screens?.length > 0 ? (
        <>
          {remoteParticipantIds.map((id) => (
            <Tile key={id} id={id} />
          ))}
          {screens.map((screen) => (
            <Tile key={screen.screenId} id={screen.session_id} isScreenShare />
          ))}
          <DailyAudio ref={audioRef} />
        </>
      ) : (
        // When there are no remote participants or screen shares
        <div className="info-box">
          <h1>Waiting for others</h1>
          <p>Invite someone by sharing this link:</p>
          <span className="room-url">{window.location.href}</span>
        </div>
      )}
    </div>
  );

  return getUserMediaError ? <UserMediaError /> : renderCallScreen();
}
