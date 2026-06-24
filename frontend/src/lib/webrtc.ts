/** Wait until ICE gathering finishes (or timeout) so the SDP offer is complete. */
export function waitForIceGatheringComplete(
  pc: RTCPeerConnection,
  timeoutMs = 4000,
): Promise<void> {
  if (pc.iceGatheringState === "complete") {
    return Promise.resolve();
  }

  return new Promise((resolve) => {
    const finish = () => {
      clearTimeout(timer);
      pc.removeEventListener("icegatheringstatechange", onChange);
      resolve();
    };

    const onChange = () => {
      if (pc.iceGatheringState === "complete") finish();
    };

    const timer = setTimeout(finish, timeoutMs);
    pc.addEventListener("icegatheringstatechange", onChange);
  });
}

export function getLocalSdp(pc: RTCPeerConnection): string {
  const sdp = pc.localDescription?.sdp?.trim();
  if (!sdp || !sdp.startsWith("v=0")) {
    throw new Error("Could not build a valid WebRTC offer. Check microphone permissions.");
  }
  return sdp;
}
