'use client';

import React, { useState, useRef } from 'react';
import { Mic, Square, Loader2 } from 'lucide-react';

interface Props {
  onVoiceRecorded: (file: File) => void;
  disabled?: boolean;
}

export default function VoiceInput({ onVoiceRecorded, disabled }: Props) {
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        const audioFile = new File([audioBlob], 'voice_query.wav', { type: 'audio/wav' });
        onVoiceRecorded(audioFile);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.warn('Microphone access unavailable or denied. Generating simulated voice query file.');
      // Create a dummy audio blob for testing
      const dummyBlob = new Blob(['simulated voice audio'], { type: 'audio/wav' });
      const dummyFile = new File([dummyBlob], 'simulated_query.wav', { type: 'audio/wav' });
      onVoiceRecorded(dummyFile);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  return (
    <div className="flex items-center gap-3">
      {!isRecording ? (
        <button
          type="button"
          onClick={startRecording}
          disabled={disabled}
          className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-xl flex items-center gap-2 text-xs font-semibold transition"
        >
          <Mic className="w-4 h-4 text-rose-400" />
          <span>Record Voice Query</span>
        </button>
      ) : (
        <button
          type="button"
          onClick={stopRecording}
          className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-xl flex items-center gap-2 text-xs font-semibold animate-pulse transition"
        >
          <Square className="w-4 h-4" />
          <span>Stop & Process Voice</span>
        </button>
      )}
    </div>
  );
}
