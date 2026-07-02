# Product Requirements

## Problem Statement

Vocabulary learning often happens across disconnected tools: dictionary websites, notes apps, flashcards, and browser bookmarks. Users need one place to look up words, save meaningful vocabulary, attach personal context, and review words over time.

## Target User

The primary user is a learner who regularly encounters unfamiliar words and wants a structured way to build long-term vocabulary. The initial internal user is Yalda, using the project both as a learning tool and as a backend engineering portfolio project.

## Core Use Cases

- Search for a word and retrieve dictionary data.
- Save a word to a personal glossary.
- Add personal notes to a saved word.
- Organize saved words with tags.
- Track learning status for each saved word.
- Review due words using spaced repetition.
- View progress over time.

## MVP Scope

- User registration and login.
- JWT-based authentication.
- Dictionary lookup through a provider abstraction.
- Persisted global word and definition data.
- Personal saved words.
- Personal notes.
- Tags.
- Basic review scheduling fields.
- Tests for core API behavior.

## Non-Goals

- Full frontend application.
- AI-generated explanations.
- Quiz modes beyond basic review tracking.
- Kubernetes or complex infrastructure.
- Microservices.
- Multiple dictionary providers in the first milestone.

## Future Scope

- Daily review queue.
- Quiz modes.
- Analytics dashboard.
- Audio pronunciation support.
- Additional dictionary providers.
- Redis caching.
- Background jobs.
- AI-assisted explanations and examples.
