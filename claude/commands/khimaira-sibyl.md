# /khimaira-sibyl — meeting audio capture + transcription via Sibyl

Use the Sibyl tool family (`mcp__khimaira__sibyl_*`) to record, transcribe, summarize, or extract action items from meeting audio. Sibyl handles the full pipeline: WAV capture → Gemini transcription → parallel summarize + extract + emotion detection.

## Steps

1. **Read `$ARGUMENTS`** for the intent and pick the right Sibyl tool:

   - *"start recording / begin meeting"* → `sibyl_record_start(output_path=...)` (optional path; defaults to `~/.local/share/sibyl/meeting_<timestamp>.wav`). Returns a `recording_id` + path + pid. **Tell the user the path explicitly so they can stop it later.**
   - *"stop / done with the meeting"* → `sibyl_record_stop(recording_id)`. Use the `recording_id` from `record_start` or `list_active_recordings`.
   - *"what's still recording"* → `sibyl_list_active_recordings`
   - *"transcribe this audio file"* (path given) → `sibyl_transcribe(audio_path)` — transcript only, no summary / extract / emotion
   - *"summarize this transcript"* (text given) → `sibyl_summarize(transcript)` — narrow, doesn't need audio
   - *"process this meeting / give me everything"* → `sibyl_process(audio_path)` — full LangGraph pipeline: transcribe → (summarize + extract_actions + detect_emotions) in parallel. Most expensive but most complete.

2. **For end-to-end meeting capture**, the canonical flow is:
   - `record_start` → user has the meeting → `record_stop(recording_id)` returns the saved path → `process(path)` runs the full pipeline → present results.

3. **For an existing audio file**, go straight to `process(path)` — Sibyl doesn't need to have recorded the audio itself.

## Skip when

- No audio source (text-only request). Sibyl doesn't generate audio from text.
- Privacy / consent isn't confirmed. The `record_start` flow records system audio + mic; never start recording without the user explicitly asking for it.

## Output expectations

- `process` returns transcript + summary + action items + speaker emotions + meeting mood. Render the summary + action items first; transcript + emotions on request.
- `transcribe` / `summarize` return only the named artifact — don't volunteer to run the full pipeline unless asked.
- Cost is non-trivial (Gemini audio model on a 30-60min meeting). Don't run the pipeline multiple times for the same file.

## Notes

- Sibyl writes to `~/.local/share/sibyl/` by default. Override via `SIBYL_OUTPUT_DIR` env var.
- The transcribe node detects speaker introductions ("Hi, I'm Joseph") and uses real names instead of "Speaker 1" downstream.
- Emotion detection uses vocal tone (pitch, pace, tension) — surfaces "notable moments" with timestamps.
- The Sibyl name comes from the Cumaean Sibyl whose body withered until only her voice remained, preserved in writing. Apt for a tool that outlives the meeting's moment.
