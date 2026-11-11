# Cortex

An AI study assistant that turns your lecture notes into a tutor: it reads your material,
teaches it back, quizzes you, and schedules reviews with spaced repetition so it actually sticks.

The point of this project: **most "AI study tools" are a chatbot in a box — Cortex is a
*system*. The LLM is one component; the real work is a database that remembers your whole
semester, a scheduler built on the science of retention, and an integration that pulls your
real deadlines in automatically.**

---

## Why I built this

From personal experience, I go to class/lecture to get a taste of the material. Most people can say that they don't fully understand the material the first time around. The method I use to actually understand the material is working with it through an LLM, but there was a couple things that were missing.

1. It was hard to keep track of which notes or reviews were for which lectures or topics. Paste a few weeks worth of notes into a chat and it's easy to get disorganize. Cortex makes it so you have a location for the notes of each topic from each lecture.
2. **The explanations disappear.** A chat is a scroll you lose. If I didn't copy an explanation
   down somewhere, it was gone, and there was no organized record of what I'd actually learned.
3. I would quiz myself weekly but at times it was easy to forget to complete my weekly quizzes and how i did on them and how it works. Cortex keeps track and schedules weekly quizzes so you know what you need to work on week by week.

Cortex is a tool that helps you stay on track with classes and material to be documented all quarter.  —
organized by class and lecture, with the explanations, definitions, and practice all kept.
Instead of re-deriving it in a fresh chat every time, it's written down, structured, and
searchable. When midterms and finals come, I'm not starting over — the whole term is already
documented.

The Canvas and calendar pieces make it **one place to run my week**: wake up, open Cortex, and
see what I need to learn and what I need to practice, with my assignments and deadlines already
pulled in.

And the part that cements it for me — a **quiz at the end of the week.** Being *tested* on what
I learned, instead of just re-reading it, is what makes it stick. That's the whole loop: learn
it, write it down, get quizzed on it, and let spaced repetition bring it back before I forget.

---

## How it works

Two pipelines: one when you add material, one every day you study.

```
INGEST A LECTURE  (when you paste notes)
──────────────────────────────────────────
Pasted lecture text
   │
   ├── chunk it if it exceeds the model's context window
   ├── LLM call → topics, each with a lesson + quiz questions
   ├── validate the output against a schema (repair / re-ask on bad JSON)
   ├── dedup topics against lectures already stored
   └── write to the database

STUDY A TOPIC  (the daily loop)
──────────────────────────────────────────
Scheduler picks what's due
   │
   ├── Learn  — read the LLM-written lesson, grounded in your lecture
   ├── Tutor  — ask follow-up questions (LLM, scoped to that topic)
   ├── Quiz   — answer the questions
   └── result → spaced-repetition scheduler sets the next review date
```

---

## Architecture

The LLM is one component. The backbone is a real backend with a database, an external
integration, and an orchestration layer around the model — that's what makes Cortex a system,
not a prompt.

```
┌──────────────────────────────┐        ┌─────────────────────────────────────────────┐
│  FRONTEND  (React/TS)        │        │  BACKEND  (Python/FastAPI)                  │
│  - paste lectures            │        │                                             │
│  - Learn / Tutor / Quiz      │ ──────▶│  • REST API                                 │
│  - planner + calendar        │        │  • Database (PostgreSQL; SQLite in dev)     │
│  - progress dashboard        │ ◀──────│      classes, lectures, topics, questions,  │
└──────────────────────────────┘        │      reviews, plan, assignments             │
                                         │  • Canvas import (assignments + due dates)  │
                                         │  • LLM orchestration: schema-constrained    │
                                         │      JSON, validate-and-repair, chunking,   │
                                         │      topic dedup                            │
                                         │  • spaced-repetition scheduler              │
                                         │  • API key in .env (never in the browser)   │
                                         └─────────────────────────────────────────────┘
                                                │                        │
                                                ▼                        ▼
                                     OpenAI / Anthropic API        Canvas LMS API
```

- **Database — the system of record.** A chat can't be this; a flat scroll of messages doesn't
  let you ask "what have I covered in CSE 142, and what am I weak on?"
- **Canvas import — the automation.** Assignments and due dates are pulled from the Canvas REST
  API on a schedule, not typed in by hand. Automatically ingesting real external data is exactly
  what a chat assistant can't do.
- **LLM orchestration — the hard part of using an LLM well.** Forcing schema-constrained JSON, a
  validate-and-repair loop for bad output, chunking long lectures, deduping overlapping topics.
- **No RAG needed (yet).** A single lecture fits in the model's context window, so ingestion
  hands it the text directly. Embeddings only appear for topic dedup; full retrieval/RAG would
  only come in for a future "ask across my whole semester" feature.

---

## Tech stack

| Layer | Tools |
|---|---|
| **Backend** | Python · FastAPI · SQLAlchemy · Pydantic |
| **Database** | PostgreSQL (SQLite in local dev), queried with SQL |
| **Frontend** | React · TypeScript · Vite |
| **AI & integrations** | OpenAI / Anthropic API · Canvas LMS API |
| **Tooling** | Git · pytest · Docker + cloud deploy *(planned)* |

---

## The LLM's job

Three jobs — two are generation (produced together when you ingest a lecture), one is live.

**1 + 2 · Learn lesson and Quiz (at ingest).** One call turns a lecture into structured data;
each topic carries both its lesson and its questions:

```json
{
  "topics": [
    {
      "name": "Gradient Descent",
      "lesson": "A 2-4 paragraph explanation grounded in the lecture...",
      "key_points": ["...", "..."],
      "questions": [
        {"q": "...", "choices": ["a","b","c","d"], "answer": 1, "explanation": "..."}
      ]
    }
  ]
}
```

The backend validates this against a schema — repairing or re-asking on malformed output —
before anything touches the database. LLMs are unreliable; the orchestration layer is what makes
them safe to build on.

**3 · Tutor (live).** A separate endpoint: a follow-up question is sent to the model with its
topic + source lecture as context, so answers stay grounded in your course instead of wandering.

All three use the same API key, held server-side in `.env`.

---

## Spaced repetition — the engine

Each topic sits in a Leitner "box" (1–5). Pass a quiz and it moves up a box and the next review
pushes further out (1 → 3 → 7 → 16 days); miss it and it drops back to box 1 and returns soon. A
forgetting-curve estimate (memory decays since the last review, slower for higher boxes) surfaces
topics that are about to slip. The scheduler is what decides, every day, what to put in front of
you — and it's a real algorithm, not a prompt.

---

## Canvas integration

Your assignments and deadlines already live in Canvas. Cortex connects via the Canvas **REST
API** (using a personal access token stored server-side), pulls your **courses, assignments, and
due dates**, and keeps them current on a periodic sync. Imported assignments land in the
database, show up on the calendar, and link to the topics you need to review to do them.

This is the piece that makes Cortex self-maintaining rather than another thing you have to feed.

---

## Status

Early, built in phases. The current focus is the backend.

- **Phase 1 — backend foundation** *(in progress)*: FastAPI app, database schema, and the
  paste-lecture → Learn + Quiz loop (LLM stubbed, then wired to a real key).
- **Phase 2 — the engine**: spaced-repetition scheduler + progress tracking.
- **Phase 3 — Tutor, planner, calendar, assignments.**
- **Phase 4 — Canvas import; React frontend; deployment.**

A clickable design mockup exists to pin down the UX; the production frontend is built last,
against the real API.

---

## Getting started

*(Filled in as the backend lands.)*

```bash
# backend
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload                        # http://127.0.0.1:8000
```