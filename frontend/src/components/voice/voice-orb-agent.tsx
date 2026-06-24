"use client";

import { useCallback, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Phone, PhoneOff } from "lucide-react";

import { CallTranscript } from "@/components/voice/call-transcript";
import { useAuth } from "@/context/auth-context";
import { api, ApiError } from "@/lib/api";
import {
  addCallRecord,
  updateCallRecord,
  type CallRecord,
} from "@/lib/call-history";
import {
  handleRealtimeTranscriptEvent,
  resetTranscriptStream,
  type TranscriptLine,
} from "@/lib/realtime-transcript";
import { getLocalSdp, waitForIceGatheringComplete } from "@/lib/webrtc";
import { cn } from "@/lib/utils";

type AgentType = "inbound" | "outbound";
type CallStatus = "idle" | "connecting" | "live" | "error";

type VoiceOrbAgentProps = {
  agentType?: AgentType;
  title?: string;
  agentName?: string;
};

const DEFAULT_AGENT_NAME = "Sara";
const END_CALL_DELAY_MS = 3500;

export function VoiceOrbAgent({
  agentType = "inbound",
  title = "Karyan Realty",
  agentName = DEFAULT_AGENT_NAME,
}: VoiceOrbAgentProps) {
  const { token } = useAuth();
  const [status, setStatus] = useState<CallStatus>("idle");
  const [statusLabel, setStatusLabel] = useState("Ready to connect");
  const [transcript, setTranscript] = useState<TranscriptLine[]>([]);
  const activeCallIdRef = useRef<string | null>(null);
  const callStartRef = useRef<number | null>(null);

  const peerConnectionRef = useRef<RTCPeerConnection | null>(null);
  const dataChannelRef = useRef<RTCDataChannel | null>(null);
  const localStreamRef = useRef<MediaStream | null>(null);
  const remoteAudioRef = useRef<HTMLAudioElement | null>(null);
  const handledCallsRef = useRef<Set<string>>(new Set());
  const pendingEndRef = useRef(false);
  const endCallTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const runTool = useCallback(
    async (name: string, args: Record<string, string | number>) => {
      if (!token) throw new Error("Not signed in");
      if (name === "search_properties") {
        return api.searchProperties(token, {
          location: args.location as string | undefined,
          bhk: args.bhk as string | undefined,
          property_type: args.property_type as string | undefined,
          max_budget_lakhs: args.max_budget_lakhs as number | undefined,
          budget: args.budget as string | undefined,
          query: args.query as string | undefined,
        });
      }
      if (name === "get_inventory_overview") {
        return api.getInventoryOverview(token);
      }
      if (name === "get_property_details") {
        return api.getPropertyDetails(token, String(args.property_id ?? ""));
      }
      if (name === "check_availability") {
        return api.checkAvailability(
          token,
          String(args.date),
          args.preferred_time != null ? String(args.preferred_time) : null,
        );
      }
      if (name === "validate_email") {
        return api.validateEmail(token, String(args.email ?? ""));
      }
      if (name === "book_meeting") {
        return api.bookMeeting(token, {
          name: String(args.name),
          email: String(args.email),
          date: String(args.date),
          time: String(args.time),
          property_id: args.property_id != null ? String(args.property_id) : undefined,
          property_name: args.property_name != null ? String(args.property_name) : undefined,
        });
      }
      if (name === "end_call") {
        return {
          success: true,
          message: "Give your closing line, then the call will end.",
        };
      }
      throw new Error(`Unknown tool: ${name}`);
    },
    [token],
  );

  const sendEvent = useCallback((event: Record<string, unknown>) => {
    const dc = dataChannelRef.current;
    if (dc?.readyState === "open") dc.send(JSON.stringify(event));
  }, []);

  const finishCallRecord = useCallback(
    (id: string | null, callStatus: CallRecord["status"]) => {
      if (!id || !callStartRef.current) return;
      const durationSec = Math.round((Date.now() - callStartRef.current) / 1000);
      updateCallRecord(id, {
        endedAt: new Date().toISOString(),
        durationSec,
        status: callStatus,
      });
      callStartRef.current = null;
      activeCallIdRef.current = null;
    },
    [],
  );

  const cleanupConnection = useCallback(() => {
    if (endCallTimerRef.current) {
      clearTimeout(endCallTimerRef.current);
      endCallTimerRef.current = null;
    }
    pendingEndRef.current = false;
    handledCallsRef.current.clear();
    resetTranscriptStream();
    dataChannelRef.current?.close();
    dataChannelRef.current = null;
    peerConnectionRef.current?.close();
    peerConnectionRef.current = null;
    localStreamRef.current?.getTracks().forEach((t) => t.stop());
    localStreamRef.current = null;
    if (remoteAudioRef.current) remoteAudioRef.current.srcObject = null;
  }, []);

  const stopCall = useCallback(
    async (failed = false) => {
      const id = activeCallIdRef.current;
      cleanupConnection();

      if (id && callStartRef.current) {
        finishCallRecord(id, failed ? "failed" : "completed");
      }
      setStatus("idle");
      setStatusLabel("Ready to connect");
    },
    [cleanupConnection, finishCallRecord],
  );

  const scheduleEndCall = useCallback(() => {
    if (endCallTimerRef.current) return;
    setStatusLabel("Goodbye — ending call…");
    endCallTimerRef.current = setTimeout(() => {
      endCallTimerRef.current = null;
      stopCall();
    }, END_CALL_DELAY_MS);
  }, [stopCall]);

  const handleFunctionCall = useCallback(
    async (item: { call_id?: string; name?: string; arguments?: string }) => {
      const callId = item.call_id;
      if (!callId || handledCallsRef.current.has(callId)) return;
      handledCallsRef.current.add(callId);

      let args: Record<string, string | number> = {};
      try {
        args = JSON.parse(item.arguments || "{}");
      } catch {
        args = {};
      }

      if (
        item.name === "search_properties" ||
        item.name === "get_property_details" ||
        item.name === "get_inventory_overview"
      ) {
        setStatusLabel("Looking up Karyan listings…");
      } else if (item.name === "check_availability") {
        setStatusLabel("Checking visit slots…");
      } else if (item.name === "validate_email") {
        setStatusLabel("Confirming your email…");
      } else if (item.name === "book_meeting") {
        setStatusLabel("Sending calendar invite…");
      } else if (item.name === "end_call") {
        setStatusLabel("Wrapping up…");
      }

      try {
        const output = await runTool(item.name ?? "", args);
        const msg = (output as { message?: string }).message;
        if (msg && activeCallIdRef.current) {
          updateCallRecord(activeCallIdRef.current, { summary: msg });
        }
        if (item.name === "end_call") {
          pendingEndRef.current = true;
        }
        sendEvent({
          type: "conversation.item.create",
          item: {
            type: "function_call_output",
            call_id: callId,
            output: JSON.stringify(output),
          },
        });
        sendEvent({ type: "response.create" });
        if (item.name === "end_call") {
          scheduleEndCall();
        } else {
          setStatusLabel("Live — ask about properties or book a visit");
        }
      } catch (error) {
        const message = error instanceof Error ? error.message : "Tool failed";
        sendEvent({
          type: "conversation.item.create",
          item: {
            type: "function_call_output",
            call_id: callId,
            output: JSON.stringify({ success: false, message }),
          },
        });
        sendEvent({ type: "response.create" });
      }
    },
    [runTool, scheduleEndCall, sendEvent],
  );

  const startCall = useCallback(async () => {
    if (!token) {
      setStatus("error");
      setStatusLabel("You must be signed in to start a call.");
      return;
    }

    setStatus("connecting");
    setStatusLabel("Connecting to agent…");
    setTranscript([]);
    resetTranscriptStream();

    const recordId = crypto.randomUUID();
    callStartRef.current = Date.now();
    activeCallIdRef.current = recordId;
    addCallRecord({
      id: recordId,
      agent: agentType,
      startedAt: new Date().toISOString(),
      status: "in-progress",
      summary: "Voice session started",
    });

    try {
      const localStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });
      localStreamRef.current = localStream;

      const pc = new RTCPeerConnection({
        iceServers: [{ urls: "stun:stun.l.google.com:19302" }],
      });
      peerConnectionRef.current = pc;

      pc.ontrack = async (e) => {
        if (!remoteAudioRef.current) return;
        remoteAudioRef.current.srcObject = e.streams[0];
        try {
          await remoteAudioRef.current.play();
        } catch {
          /* user gesture already provided */
        }
      };

      localStream.getTracks().forEach((t) => pc.addTrack(t, localStream));

      const dc = pc.createDataChannel("oai-events");
      dataChannelRef.current = dc;

      dc.onopen = () => {
        sendEvent({
          type: "response.create",
          response: {
            output_modalities: ["audio"],
            instructions: `Greet in English only as Sara from Karyan Realty NCR. Say: "Hi, thank you for calling Karyan — I'm Sara. How can I help you find a home today?" Never use Hindi. Keep it warm and brief.`,
          },
        });
      };

      dc.onmessage = (msg) => {
        try {
          const event = JSON.parse(msg.data) as Record<string, unknown>;
          handleRealtimeTranscriptEvent(event, {
            onLinesChange: setTranscript,
          });
          const item = event.item as
            | { type?: string; call_id?: string; name?: string; arguments?: string }
            | undefined;
          if (event.type === "response.output_item.done" && item?.type === "function_call") {
            handleFunctionCall(item);
          }
          if (event.type === "response.function_call_arguments.done") {
            handleFunctionCall({
              call_id: event.call_id as string,
              name: event.name as string,
              arguments: event.arguments as string,
            });
          }
          if (event.type === "input_audio_buffer.speech_started") {
            setStatusLabel("Listening…");
          }
          if (event.type === "input_audio_buffer.speech_stopped") {
            setStatusLabel("Agent is responding…");
          }
          if (event.type === "response.audio.done" || event.type === "response.done") {
            if (pendingEndRef.current && !endCallTimerRef.current) {
              scheduleEndCall();
            } else if (!pendingEndRef.current) {
              setStatusLabel("Live — ask about properties or book a visit");
            }
          }
          if (event.type === "error") {
            setStatus("error");
            const err = event.error as { message?: string } | undefined;
            setStatusLabel(err?.message || "Connection error");
          }
        } catch {
          /* ignore malformed events */
        }
      };

      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);
      await waitForIceGatheringComplete(pc);

      const localSdp = getLocalSdp(pc);
      const answerSdp = await api.createVoiceSession(localSdp, token);
      await pc.setRemoteDescription({ type: "answer", sdp: answerSdp });

      setStatus("live");
      setStatusLabel("Live — ask about properties or book a visit");
      updateCallRecord(recordId, { summary: "Connected — scheduling via voice" });
    } catch (error) {
      cleanupConnection();
      const message =
        error instanceof ApiError
          ? error.message
          : error instanceof Error
            ? error.message
            : "Connection failed";
      finishCallRecord(recordId, "failed");
      setStatus("error");
      setStatusLabel(message);
    }
  }, [
    agentType,
    cleanupConnection,
    finishCallRecord,
    handleFunctionCall,
    scheduleEndCall,
    sendEvent,
    token,
  ]);

  const isLive = status === "live";
  const isConnecting = status === "connecting";
  const canStart = status === "idle" || status === "error";
  const showTranscript = isLive || isConnecting || transcript.length > 0;

  return (
    <div className="flex h-full flex-col overflow-hidden px-4 py-5 sm:px-6">
      <audio ref={remoteAudioRef} autoPlay playsInline className="hidden" />

      <div className="relative z-10 mx-auto flex w-full max-w-xl flex-1 flex-col items-center overflow-hidden">
        {/* Fixed header + orb */}
        <div className="flex w-full shrink-0 flex-col items-center">
          <p className="mb-1 text-xs font-medium uppercase tracking-[0.2em] text-[#ff3c00]/80 font-space">
            {title}
          </p>
          <h1 className="text-center font-inter text-xl font-medium tracking-tight text-white sm:text-2xl">
            Talk with{" "}
            <span className="font-instrument italic text-[#ff3c00]">{agentName}</span>
          </h1>

          <div className="relative mt-5 flex h-[220px] w-[220px] shrink-0 items-center justify-center sm:mt-6 sm:h-[240px] sm:w-[240px]">
            <AnimatePresence>
              {(isLive || isConnecting) &&
                [0, 1, 2].map((i) => (
                  <motion.div
                    key={`ring-${i}`}
                    className="absolute inset-0 rounded-full border border-[#ff3c00]/20"
                    initial={{ scale: 0.9, opacity: 0.45 }}
                    animate={{ scale: 1.35, opacity: 0 }}
                    transition={{
                      duration: isConnecting ? 1.2 : 2,
                      repeat: Infinity,
                      delay: i * 0.5,
                      ease: "easeOut",
                    }}
                  />
                ))}
            </AnimatePresence>

            <motion.button
              type="button"
              onClick={canStart ? startCall : undefined}
              disabled={isConnecting || isLive}
              animate={{ scale: isLive ? [1, 1.03, 1] : 1 }}
              transition={{
                scale: { duration: 1.6, repeat: isLive ? Infinity : 0, ease: "easeInOut" },
              }}
              className={cn(
                "relative z-10 h-40 w-40 rounded-full sm:h-44 sm:w-44",
                "bg-gradient-to-br from-[#ff3c00] via-orange-500 to-amber-600",
                "shadow-[0_0_50px_-10px_rgba(255,60,0,0.5)]",
                "before:absolute before:inset-0 before:rounded-full before:bg-gradient-to-t before:from-black/20 before:to-white/20",
                canStart && "cursor-pointer hover:shadow-[0_0_60px_-8px_rgba(255,60,0,0.6)]",
                (isConnecting || isLive) && "cursor-default",
              )}
            >
              <span className="sr-only">Start call</span>
              <span className="absolute left-[18%] top-[14%] h-14 w-14 rounded-full bg-white/25 blur-xl" />
            </motion.button>
          </div>

          <motion.p
            key={statusLabel}
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            className={cn(
              "mt-3 min-h-[2rem] max-w-sm text-center text-sm font-space",
              status === "error" ? "text-red-300" : "text-gray-400",
            )}
          >
            {statusLabel}
          </motion.p>

          <div className="mt-3 flex shrink-0 items-center gap-3">
            {canStart && (
              <button
                type="button"
                onClick={startCall}
                className="inline-flex h-10 items-center gap-2 rounded-full bg-white px-6 text-sm font-semibold text-black transition-colors hover:bg-gray-100 font-space"
              >
                <Phone className="h-4 w-4" />
                Start call
              </button>
            )}

            {isConnecting && (
              <button
                type="button"
                disabled
                className="inline-flex h-10 items-center rounded-full bg-white/10 px-6 text-sm text-white font-space"
              >
                Connecting…
              </button>
            )}

            {isLive && (
              <button
                type="button"
                onClick={() => stopCall()}
                className="inline-flex h-10 items-center gap-2 rounded-full border border-red-500/40 px-6 text-sm text-red-300 transition-colors hover:bg-red-500/10 font-space"
              >
                <PhoneOff className="h-4 w-4" />
                End call
              </button>
            )}
          </div>
        </div>

        {/* Scrollable transcript below orb */}
        {showTranscript && (
          <CallTranscript
            lines={transcript}
            agentName={agentName}
            active={isLive || isConnecting}
            className="mt-4 min-h-0 w-full flex-1"
          />
        )}

        {!showTranscript && (
          <p className="mt-6 shrink-0 text-center text-[11px] text-gray-600 font-space">
            Karyan Realty · Site visits Mon–Fri 9 AM–9 PM IST · Google Calendar + Meet
          </p>
        )}
      </div>
    </div>
  );
}
