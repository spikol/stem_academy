# About

This repo holds the materials for a workshop series run by **Daniel Spikol**
at **DIKU (Department of Computer Science, University of Copenhagen) and the
Center for Digital Education**: *"Why Playful AI with IoT and Generative
AI?"* — part of a broader strand on **didactic transposition and AI
literacy**.

## The idea

The workshops treat micro:bit, Teachable Machine, and Claude as a hands-on
route into AI literacy, rather than teaching AI concepts in the abstract.
Participants build and play with small, physical, sensor-driven systems —
training a Teachable Machine model from a micro:bit's inputs, asking an
LLM yes/no questions through a micro:bit card-deck interface, streaming
live sensor data to a browser dashboard — and use that hands-on experience
as the basis for discussing what AI is, what it isn't, and how these ideas
transpose into a classroom.

The framing draws on **playful learning**: curiosity, tinkering, and
hacking as legitimate ways to build understanding, not just a warm-up
before the "real" content.

## Who it's for

Educators and students engaging with AI literacy through the DIKU / Center
for Digital Education seminar series — the sessions are pitched at people
encountering these tools for the first time, not requiring a programming
background going in.

## What's actually in here

A mix of:
- **Slide decks** (Marp/Markdown) for each seminar session.
- **Working code**: a Flask backend + browser frontend that lets a
  micro:bit ask Claude questions over USB, and a live sensor-streaming
  dashboard.
- **Planning notes** behind the sessions (`org_notes/`).
- **Device firmware/scripts** for the micro:bit side of each activity
  (`dev/`).

See [README.md](README.md) for how the pieces fit together and how to run
each one.
