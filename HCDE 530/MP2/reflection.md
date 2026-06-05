# Reflection — Research Analyzer

## What did I build?

Research Analyzer is a web-based tool for UX researchers who need to make sense
of usability session data. You upload your transcripts and session notes, type in
an optional research focus, and the tool runs them through the Claude API to
extract recurring themes, pull verbatim quotes, and identify which sessions each
theme appeared in. The output is a four-tab Excel spreadsheet covering theme
summaries, quotes with timestamps, session-level summaries, and the raw analysis
data. The whole thing runs in a browser through Streamlit, so there is nothing to
install. The problem it solves is real: after a round of usability testing,
researchers often spend as much time organizing and coding transcripts as they did
running the sessions. This tool handles that first pass so researchers can focus
on interpretation rather than sorting.

## What decisions did I make?

The two biggest decisions were platform and scope. I chose Python and Streamlit
over a browser-only tool because the core work is computation, not interface. The
tool needs to parse files, call an API, and write structured Excel output, and
Python handles all of that cleanly. Streamlit gave me a working browser UI without
having to build a separate frontend.

On scope, I deliberately left out audio and video transcription. It would have
made the tool more powerful but also significantly more complex to build and more
expensive to run. Keeping v1 to text-only meant I could ship something that
actually works rather than something half-finished.

The other meaningful decision was the two-pass API structure. Rather than sending
all transcripts to Claude in one call, pass one analyzes each session individually
and pass two synthesizes across sessions. This keeps the per-call token count
manageable and produces cleaner theme attribution since Claude is focused on one
session at a time before being asked to generalize.

## What would I do differently?

The biggest thing I would change is how the tool handles long transcripts. Right
now a very long session file gets sent to the API in one piece, which risks hitting
token limits and can produce shallower analysis because Claude is working through
too much text at once. If I built this again I would add a chunking step in
utils.py that splits long transcripts into overlapping segments, analyzes each
chunk, and then merges the themes before passing them to the cross-session
synthesis. It is more complex to implement but would make the tool reliable across
a much wider range of real-world transcript lengths.

## What does this work demonstrate?

This project touches three areas in a connected way. On the API and data side, it
shows I can work with a real external API, structure prompts to return predictable
JSON, handle failure cases gracefully, and manage sensitive credentials correctly
through environment variables and secrets management. The two-pass prompt design
in analyzer.py reflects an understanding that what you ask the model to do and how
you structure that ask directly affects the quality of what you get back.

On the code literacy side, the project is split into four files each with a single
job, which made it possible to test each piece before wiring them together. Adding
the timestamp feature mid-build required coordinated changes across utils.py,
analyzer.py, and exporter.py, and updating the spec before touching any code
meant those changes were intentional rather than reactive.

On the tool-building side, the interface follows the actual workflow a researcher
goes through: upload, configure, run, download. The decisions about what to leave
out of v1 were as important as what went in.