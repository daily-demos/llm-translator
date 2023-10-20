import React, { useCallback, useState, useContext, useEffect } from 'react';
import {
  useLocalParticipant,
  useDevices,
  useDaily,
  useDailyEvent,
  DailyVideo,
} from '@daily-co/daily-react';
import UserMediaError from '../UserMediaError/UserMediaError';

import './HairCheck.css';
import { LanguageContext } from '../../contexts/Language/LanguageContext';

export default function HairCheck({ joinCall, cancelCall }) {
  const localParticipant = useLocalParticipant();
  const { microphones, speakers, cameras, setMicrophone, setCamera, setSpeaker } = useDevices();
  const callObject = useDaily();

  const [getUserMediaError, setGetUserMediaError] = useState(false);
  const [lang, setLang] = useContext(LanguageContext);
  useDailyEvent(
    'camera-error',
    useCallback(() => {
      setGetUserMediaError(true);
    }, []),
  );

  const onChange = (e) => {
    callObject.setUserName(e.target.value);
  };

  const join = (e) => {
    e.preventDefault();
    joinCall();
  };

  useEffect(() => {
    console.log('in hair check, lang changed to: ', lang);
  }, [lang]);

  const updateMicrophone = (e) => {
    setMicrophone(e.target.value);
  };

  const updateSpeakers = (e) => {
    setSpeaker(e.target.value);
  };

  const updateCamera = (e) => {
    setCamera(e.target.value);
  };

  const updateSubtitleLanguage = (e) => {
    console.log('setting subtitle language', e.target.value);
    setLang({ audio: lang.audio, subtitles: e.target.value });
  };

  const updateAudioLanguage = (e) => {
    console.log('setting audio language', e.target.value);

    setLang({ audio: e.target.value, subtitles: lang.subtitles });
  };

  return getUserMediaError ? (
    <UserMediaError />
  ) : (
    <form className="hair-check" onSubmit={join}>
      <h1>Setup your hardware</h1>
      {/* Video preview */}
      {localParticipant && <DailyVideo sessionId={localParticipant.session_id} mirror />}

      {/* Username */}
      <div>
        <label htmlFor="username">Your name:</label>
        <input
          name="username"
          type="text"
          placeholder="Enter username"
          onChange={(e) => onChange(e)}
          value={localParticipant?.user_name || ' '}
        />
      </div>

      {/* Microphone select */}
      <div>
        <label htmlFor="micOptions">Microphone:</label>
        <select name="micOptions" id="micSelect" onChange={updateMicrophone}>
          {microphones?.map((mic) => (
            <option key={`mic-${mic.device.deviceId}`} value={mic.device.deviceId}>
              {mic.device.label}
            </option>
          ))}
        </select>
      </div>

      {/* Speakers select */}
      <div>
        <label htmlFor="speakersOptions">Speakers:</label>
        <select name="speakersOptions" id="speakersSelect" onChange={updateSpeakers}>
          {speakers?.map((speaker) => (
            <option key={`speaker-${speaker.device.deviceId}`} value={speaker.device.deviceId}>
              {speaker.device.label}
            </option>
          ))}
        </select>
      </div>

      {/* Camera select */}
      <div>
        <label htmlFor="cameraOptions">Camera:</label>
        <select name="cameraOptions" id="cameraSelect" onChange={updateCamera}>
          {cameras?.map((camera) => (
            <option key={`cam-${camera.device.deviceId}`} value={camera.device.deviceId}>
              {camera.device.label}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="subtitleLanguage">Subtitle language:</label>
        <select
          name="subtitleLanguage"
          id="subtitleLanguageSelect"
          onChange={updateSubtitleLanguage}
          value={lang.subtitles}>
          <option key="english" value="english">
            English
          </option>
          <option key="french" value="french">
            French
          </option>
        </select>
      </div>
      <div>
        <label htmlFor="audioLanguage">Audio language:</label>
        <select
          name="audioLanguage"
          id="audioLanguageSelect"
          onChange={updateAudioLanguage}
          value={lang.audio}>
          <option key="english" value="english">
            English
          </option>
          <option key="french" value="french">
            French
          </option>
        </select>
      </div>

      <button onClick={join} type="submit">
        Join call
      </button>
      <button onClick={cancelCall} className="cancel-call" type="button">
        Back to start
      </button>
    </form>
  );
}
