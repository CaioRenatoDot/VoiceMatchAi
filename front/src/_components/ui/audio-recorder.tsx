"use client";

import { useState, useRef, useEffect } from "react";
import { Mic, Square, AlertCircle } from "lucide-react";
import { Button } from "./button";
import { cn } from "@/lib/utils";

interface AudioRecorderProps {
  onRecordingComplete: (blob: Blob) => void;
  disabled?: boolean;
}

export function AudioRecorder({ onRecordingComplete, disabled }: AudioRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [duration, setDuration] = useState(0);
  const [error, setError] = useState<string | null>(null);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  async function startRecording() {
    setError(null);
    chunksRef.current = [];
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Determine mimeType (audio/webm is standard and widely supported, with audio/ogg as fallback)
      let options = { mimeType: "audio/webm" };
      if (!MediaRecorder.isTypeSupported("audio/webm")) {
        options = { mimeType: "audio/ogg" };
      }
      
      const mediaRecorder = new MediaRecorder(stream, options);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(chunksRef.current, { type: options.mimeType });
        onRecordingComplete(audioBlob);
        
        // Stop all tracks on the stream to release the mic
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setDuration(0);
      
      timerRef.current = setInterval(() => {
        setDuration((prev) => prev + 1);
      }, 1000);
      
    } catch (err: any) {
      console.error("Error accessing microphone:", err);
      setError("Não foi possível acessar o microfone. Verifique as permissões do seu navegador.");
    }
  }

  function stopRecording() {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  }

  function formatTime(secs: number) {
    const mins = Math.floor(secs / 60);
    const remainingSecs = secs % 60;
    return `${mins}:${remainingSecs.toString().padStart(2, "0")}`;
  }

  return (
    <div className="flex flex-col items-center gap-3">
      {error && (
        <div className="flex items-center gap-2 text-sm text-destructive bg-destructive/10 p-3 rounded-xl border border-destructive/20 max-w-md">
          <AlertCircle className="size-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}
      
      <div className="flex items-center gap-4">
        {isRecording ? (
          <div className="flex items-center gap-4 rounded-full bg-red-500/10 px-4 py-2 border border-red-500/20 shadow-inner">
            <span className="relative flex size-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full size-3 bg-red-500"></span>
            </span>
            <span className="text-sm font-mono font-medium text-red-500">
              Gravando... {formatTime(duration)}
            </span>
            <Button
              type="button"
              variant="destructive"
              size="icon"
              onClick={stopRecording}
              className="rounded-full shadow-lg hover:shadow-red-500/20 h-8 w-8"
            >
              <Square className="size-3 fill-current" />
            </Button>
          </div>
        ) : (
          <Button
            type="button"
            disabled={disabled}
            onClick={startRecording}
            className={cn(
              "rounded-full px-6 py-6 shadow-md transition-all hover:scale-105 active:scale-95 text-base font-semibold",
              "bg-gradient-to-r from-sidebar-primary to-blue-600 hover:from-sidebar-primary/90 hover:to-blue-700"
            )}
          >
            <Mic className="size-5 mr-2" />
            Responder por Áudio
          </Button>
        )}
      </div>
    </div>
  );
}
