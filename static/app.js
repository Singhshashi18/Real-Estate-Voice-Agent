const startBtn = document.getElementById("start-btn");
const stopBtn = document.getElementById("stop-btn");
const statusDot = document.getElementById("status-dot");
const statusLabel = document.getElementById("status-label");
const statusDetail = document.getElementById("status-detail");
const logEl = document.getElementById("log");
const remoteAudio = document.getElementById("remote-audio");

let peerConnection = null;
let dataChannel = null;
let localStream = null;
const handledCalls = new Set();

function setStatus(state, label, detail) {
  statusDot.className = `status-dot ${state}`;
  statusLabel.textContent = label;
  statusDetail.textContent = detail;
}

function addLog(message, level = "info") {
  const entry = document.createElement("div");
  entry.className = "log-entry";
  entry.innerHTML = `<strong>[${level}]</strong> ${message}`;
  logEl.prepend(entry);
}

async function runTool(name, args) {
  if (name === "check_availability") {
    const response = await fetch("/api/tools/check-availability", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        date: args.date,
        preferred_time: args.preferred_time ?? null,
      }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Availability check failed");
    }
    return data;
  }

  if (name === "book_meeting") {
    const response = await fetch("/api/tools/book-meeting", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: args.name,
        email: args.email,
        date: args.date,
        time: args.time,
      }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Booking failed");
    }
    return data;
  }

  throw new Error(`Unknown tool: ${name}`);
}

function sendEvent(event) {
  if (!dataChannel || dataChannel.readyState !== "open") {
    return;
  }
  dataChannel.send(JSON.stringify(event));
}

async function handleFunctionCall(item) {
  const callId = item.call_id;
  if (!callId || handledCalls.has(callId)) {
    return;
  }
  handledCalls.add(callId);
  const name = item.name;
  let args = {};

  try {
    args = JSON.parse(item.arguments || "{}");
  } catch {
    args = {};
  }

  addLog(`Tool call: ${name}(${JSON.stringify(args)})`);

  try {
    const output = await runTool(name, args);
    addLog(`Tool result: ${output.message || JSON.stringify(output)}`, "tool");

    sendEvent({
      type: "conversation.item.create",
      item: {
        type: "function_call_output",
        call_id: callId,
        output: JSON.stringify(output),
      },
    });
    sendEvent({ type: "response.create" });
  } catch (error) {
    const message = error.message || "Tool execution failed";
    addLog(message, "error");

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
}

function handleRealtimeEvent(event) {
  switch (event.type) {
    case "response.output_item.done": {
      const item = event.item;
      if (item?.type === "function_call") {
        handleFunctionCall(item);
      }
      break;
    }
    case "response.function_call_arguments.done": {
      handleFunctionCall({
        call_id: event.call_id,
        name: event.name,
        arguments: event.arguments,
      });
      break;
    }
    case "error":
      addLog(event.error?.message || "Realtime API error", "error");
      setStatus("error", "Error", event.error?.message || "Realtime API error");
      break;
    case "session.created":
      addLog("Realtime session created");
      break;
    case "input_audio_buffer.speech_started":
      setStatus("live", "Listening", "Caller is speaking...");
      break;
    case "input_audio_buffer.speech_stopped":
      setStatus("live", "Thinking", "Agent is responding...");
      break;
    default:
      break;
  }
}

async function startCall() {
  startBtn.disabled = true;
  setStatus("connecting", "Connecting", "Requesting session and microphone...");

  try {
    localStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    peerConnection = new RTCPeerConnection();

    peerConnection.ontrack = (event) => {
      remoteAudio.srcObject = event.streams[0];
    };

    localStream.getTracks().forEach((track) => {
      peerConnection.addTrack(track, localStream);
    });

    dataChannel = peerConnection.createDataChannel("oai-events");
    dataChannel.onmessage = (message) => {
      try {
        const event = JSON.parse(message.data);
        handleRealtimeEvent(event);
      } catch {
        addLog("Received non-JSON realtime event", "error");
      }
    };

    const offer = await peerConnection.createOffer();
    await peerConnection.setLocalDescription(offer);

    const sdpResponse = await fetch("/api/session", {
      method: "POST",
      headers: { "Content-Type": "application/sdp" },
      body: offer.sdp,
    });

    const answerSdp = await sdpResponse.text();
    if (!sdpResponse.ok) {
      throw new Error(answerSdp || "Failed to create realtime session");
    }

    await peerConnection.setRemoteDescription({
      type: "answer",
      sdp: answerSdp,
    });

    stopBtn.disabled = false;
    setStatus("live", "Live", "Speak naturally to schedule a meeting.");
    addLog("Voice call connected");
  } catch (error) {
    addLog(error.message, "error");
    setStatus("error", "Failed", error.message);
    await stopCall(false);
    startBtn.disabled = false;
  }
}

async function stopCall(enableStart = true) {
  handledCalls.clear();
  if (dataChannel) {
    dataChannel.close();
    dataChannel = null;
  }

  if (peerConnection) {
    peerConnection.close();
    peerConnection = null;
  }

  if (localStream) {
    localStream.getTracks().forEach((track) => track.stop());
    localStream = null;
  }

  remoteAudio.srcObject = null;
  stopBtn.disabled = true;
  if (enableStart) {
    startBtn.disabled = false;
    setStatus("idle", "Disconnected", "Call ended. Start again when ready.");
    addLog("Call ended");
  }
}

startBtn.addEventListener("click", startCall);
stopBtn.addEventListener("click", () => stopCall(true));
