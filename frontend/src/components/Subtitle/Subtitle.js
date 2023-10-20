import './Subtitle.css';
import { useParticipantProperty, useAppMessage } from '@daily-co/daily-react';
import { useState, useContext } from 'react';
import { LanguageContext } from '../../contexts/Language/LanguageContext';

export default function Subtitle({ id }) {
  const [text, setText] = useState();
  const [lang, setLang] = useContext(LanguageContext);

  const sendAppMessage = useAppMessage({
    onAppMessage: (ev) => {
      console.log('lang: ', lang);

      if (
        lang.subtitles === 'english' &&
        ev.fromId === 'transcription' &&
        ev.data.session_id === id
      ) {
        console.log('got transcription message: ', ev.data.text);
        setText(ev.data.text);
      } else if (lang.subtitles === 'french' && ev.data?.session_id === id) {
        console.log('got FRENCH transcription message: ', ev.data.translation);
        setText(ev.data.translation);
      }
    },
  });

  return (
    <div className="subtitle">
      <p>{text && <span>{text}</span>}</p>
    </div>
  );
}
