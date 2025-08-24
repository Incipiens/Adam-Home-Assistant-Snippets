###### This is an adjoining server for the LED matrix now playing display. ######


import argparse
import asyncio
import json
import os
import sys
import tempfile
import time
from datetime import datetime, timezone
import uuid

import numpy as np
import sounddevice as sd
import soundfile as sf
import paho.mqtt.client as mqtt
from shazamio import Shazam

def record_wav(path: str, seconds: float, samplerate: int, channels: int, device: int | None):
    frames = int(seconds * samplerate)
    recording = sd.rec(frames, samplerate=samplerate, channels=channels, dtype="int16", device=device)
    sd.wait()
    sf.write(path, recording, samplerate, subtype="PCM_16")


# Limited length
def gen_client_id(prefix: str = "np") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:19]}"

def extract_track_info(result: dict) -> dict | None:
    if not result:
        return None
    track = result.get("track") or {}
    if not track:
        return None

    title = track.get("title")
    artist = track.get("subtitle")
    url = track.get("url")
    key = track.get("key")
    images = track.get("images") or {}
    cover = images.get("coverart") or images.get("background")

    album = None
    isrc = track.get("isrc")
    released = None
    # Pulling data if present
    for sec in track.get("sections", []):
        for meta in sec.get("metadata", []):
            if meta.get("title") == "Album":
                album = meta.get("text")
            if meta.get("title") == "Released":
                released = meta.get("text")

    if not (title and artist):
        return None

    return {
        "title": title,
        "artist": artist,
        "album": album,
        "released": released,
        "url": url,
        "cover": cover,
        "key": key,
        "isrc": isrc,
    }

class NowPlayingMQTT:
    def __init__(
        self,
        host: str,
        port: int,
        topic: str,
        username: str | None,
        password: str | None,
        client_id: str | None,
        qos: int = 1,
        retain: bool = False,
    ):
        self.host = host
        self.port = port
        self.topic = topic
        self.qos = qos
        self.retain = retain

        self.client = mqtt.Client(client_id=client_id or gen_client_id())

        if username:
            self.client.username_pw_set(username, password or None)

        # Last will
        self.client.will_set(self.topic, payload=b"", qos=self.qos, retain=False)

    def connect(self):
        self.client.connect(self.host, self.port, keepalive=60)
        self.client.loop_start()

    def publish(self, payload: dict):
        self.client.publish(self.topic, json.dumps(payload, ensure_ascii=False), qos=self.qos, retain=self.retain)

    def close(self):
        try:
            self.client.loop_stop()
        finally:
            self.client.disconnect()

async def run_loop(
    mqtt_client: NowPlayingMQTT,
    duration: float,
    samplerate: int,
    channels: int,
    device: int | None,
    poll_interval: float,
):
    shazam = Shazam()
    last_track_id = None

    while True:
        with tempfile.NamedTemporaryFile(prefix="now_playing_", suffix=".wav", delete=False) as tf:
            temp_path = tf.name
        try:
            record_wav(temp_path, duration, samplerate, channels, device)

            # Poll
            try:
                result = await shazam.recognize(temp_path)
            except Exception as e:
                print(f"Shazam identify failed: {e}", file=sys.stderr)
                result = None

            info = extract_track_info(result or {})
            if info:
                # Deduplicate on stable ID if possible
                track_id = info.get("key") or f"{(info.get('artist') or '').lower()} - {(info.get('title') or '').lower()}"
                if track_id != last_track_id:
                    payload = {
                        "event": "now_playing",
                        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                        "track": info,
                        "track_id": track_id,
                        "source": "microphone/shazam",
                    }
                    mqtt_client.publish(payload)
                    last_track_id = track_id
                    print(f"Published: {info['artist']} — {info['title']}")
                else:
                    print("Same track; not publishing.")
            else:
                print("No match.")
        finally:
            try:
                os.remove(temp_path)
            except Exception:
                pass

        await asyncio.sleep(poll_interval)

def env_default(name: str, fallback):
    return os.environ.get(name, fallback)

## Allows for environment-based configuration
def parse_args():
    p = argparse.ArgumentParser(description="Identify currently playing track and publish to MQTT.")
    p.add_argument("--host", default=env_default("MQTT_HOST", "127.0.0.1"), help="MQTT broker host")
    p.add_argument("--port", type=int, default=int(env_default("MQTT_PORT", 1883)), help="MQTT broker port")
    p.add_argument("--topic", default=env_default("MQTT_TOPIC", "media/now_playing"), help="MQTT topic")
    p.add_argument("--username", default=env_default("MQTT_USER", None), help="MQTT username")
    p.add_argument("--password", default=env_default("MQTT_PASS", None), help="MQTT password")
    p.add_argument("--client-id", default=env_default("MQTT_CLIENT_ID", None), help="MQTT client ID")
    p.add_argument("--qos", type=int, choices=[0, 1, 2], default=int(env_default("MQTT_QOS", 1)), help="MQTT QoS")
    p.add_argument("--retain", action="store_true", help="Retain last published message")
    p.add_argument("--duration", type=float, default=float(env_default("CAPTURE_SECONDS", 7.0)), help="Seconds to record")
    p.add_argument("--samplerate", type=int, default=int(env_default("SAMPLE_RATE", 44100)), help="Recording sample rate")
    p.add_argument("--channels", type=int, default=int(env_default("CHANNELS", 1)), help="Number of channels")
    p.add_argument("--device", type=int, default=None, help="Sounddevice input device index (default: system default)")
    p.add_argument("--interval", type=float, default=float(env_default("POLL_INTERVAL", 8.0)), help="Seconds between attempts")

    return p.parse_args()

async def main():
    args = parse_args()
    mqtt_client = NowPlayingMQTT(
        host=args.host,
        port=args.port,
        topic=args.topic,
        username=args.username,
        password=args.password,
        client_id=args.client_id,
        qos=args.qos,
        retain=args.retain,
    )

    try:
        mqtt_client.connect()
        await run_loop(
            mqtt_client,
            duration=args.duration,
            samplerate=args.samplerate,
            channels=args.channels,
            device=args.device,
            poll_interval=args.interval,
        )
    except KeyboardInterrupt:
        print("\nExiting.")
    finally:
        mqtt_client.close()

if __name__ == "__main__":
    # https://docs.python.org/3/library/asyncio-policy.html#asyncio.DefaultEventLoopPolicy This may no longer be necessary as of Python 3.8, but I took it from my old code and it works. Feel free to remove.
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
