export type TranscriptRole = "user" | "assistant";

export type TranscriptLine = {
  id: string;
  role: TranscriptRole;
  text: string;
  streaming?: boolean;
};

type TranscriptHandlers = {
  onLinesChange: (updater: (prev: TranscriptLine[]) => TranscriptLine[]) => void;
};

let streamingAssistantId: string | null = null;

function appendLine(
  handlers: TranscriptHandlers,
  role: TranscriptRole,
  text: string,
) {
  const trimmed = text.trim();
  if (!trimmed) return;
  handlers.onLinesChange((prev) => [
    ...prev,
    { id: crypto.randomUUID(), role, text: trimmed },
  ]);
}

function appendDelta(handlers: TranscriptHandlers, delta: string) {
  if (!delta) return;
  if (!streamingAssistantId) {
    streamingAssistantId = crypto.randomUUID();
    handlers.onLinesChange((prev) => [
      ...prev,
      { id: streamingAssistantId!, role: "assistant", text: delta, streaming: true },
    ]);
    return;
  }
  const id = streamingAssistantId;
  handlers.onLinesChange((prev) =>
    prev.map((line) =>
      line.id === id ? { ...line, text: line.text + delta, streaming: true } : line,
    ),
  );
}

function finalizeStreaming(handlers: TranscriptHandlers, text?: string) {
  if (!streamingAssistantId) {
    if (text?.trim()) appendLine(handlers, "assistant", text);
    return;
  }
  const id = streamingAssistantId;
  streamingAssistantId = null;
  handlers.onLinesChange((prev) =>
    prev.map((line) =>
      line.id === id
        ? { ...line, text: (text?.trim() || line.text).trim(), streaming: false }
        : line,
    ),
  );
}

export function resetTranscriptStream() {
  streamingAssistantId = null;
}

export function handleRealtimeTranscriptEvent(
  event: Record<string, unknown>,
  handlers: TranscriptHandlers,
) {
  const type = String(event.type ?? "");

  if (type === "response.output_audio_transcript.delta" || type === "response.audio_transcript.delta") {
    appendDelta(handlers, String(event.delta ?? ""));
    return;
  }

  if (
    type === "response.output_audio_transcript.done" ||
    type === "response.audio_transcript.done"
  ) {
    finalizeStreaming(handlers, String(event.transcript ?? ""));
    return;
  }

  if (type === "conversation.item.input_audio_transcription.completed") {
    appendLine(handlers, "user", String(event.transcript ?? ""));
    return;
  }

  if (type === "conversation.item.created") {
    const item = event.item as Record<string, unknown> | undefined;
    if (!item || item.role !== "user") return;
    const content = item.content as Array<Record<string, unknown>> | undefined;
    if (!content) return;
    for (const part of content) {
      if (part.type === "input_audio" && part.transcript) {
        appendLine(handlers, "user", String(part.transcript));
      }
      if (part.type === "input_text" && part.text) {
        appendLine(handlers, "user", String(part.text));
      }
    }
    return;
  }

  if (type === "response.output_item.done") {
    const item = event.item as Record<string, unknown> | undefined;
    if (item?.type === "message" && item.role === "assistant") {
      const content = item.content as Array<Record<string, unknown>> | undefined;
      if (content) {
        for (const part of content) {
          if (part.transcript) {
            finalizeStreaming(handlers, String(part.transcript));
          } else if (part.text) {
            finalizeStreaming(handlers, String(part.text));
          }
        }
      }
    }
  }
}
