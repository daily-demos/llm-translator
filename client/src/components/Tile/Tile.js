import './Tile.css';
import {
  DailyVideo,
  useMediaTrack,
  DailyAudioTrack,
  useParticipantProperty,
} from '@daily-co/daily-react';
import Username from '../Username/Username';
import Subtitle from '../Subtitle/Subtitle';

export default function Tile({ id, isScreenShare, isLocal, isAlone }) {
  const videoState = useMediaTrack(id, 'video');
  const username = useParticipantProperty(id, 'user_name');

  let containerCssClasses = isScreenShare ? 'tile-screenshare' : 'tile-video';

  if (isLocal) {
    containerCssClasses += ' self-view';
    if (isAlone) {
      containerCssClasses += ' alone';
    }
  }

  /* If a participant's video is muted, hide their video and
  add a different background color to their tile. */
  if (videoState.isOff) {
    containerCssClasses += ' no-video';
  }

  return (
    <>
      {!username.match(/^tb-/) && (
        <div className={containerCssClasses}>
          <DailyVideo
            automirror
            sessionId={id}
            type={isScreenShare ? 'screenVideo' : 'video'}
            fit="cover"
          />
          <Username id={id} isLocal={isLocal} />
          <Subtitle id={id} />
        </div>
      )}
    </>
  );
}
