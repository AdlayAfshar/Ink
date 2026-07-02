# API Design

This document outlines planned endpoints. The foundation phase only implements `/` and `/health`.

## Auth

- `POST /auth/register`: create a user account.
- `POST /auth/login`: authenticate and return access token.
- `GET /auth/me`: return the current authenticated user.

## Dictionary

- `GET /dictionary/lookup/{word}`: look up a word from cached data or an external provider.
- `GET /dictionary/words/{word_id}`: retrieve stored dictionary data for a word.

## User Glossary

- `GET /glossary/words`: list the current user's saved words.
- `POST /glossary/words`: save a word to the user's glossary.
- `GET /glossary/words/{user_word_id}`: retrieve one saved word.
- `PATCH /glossary/words/{user_word_id}`: update learning status or metadata.
- `DELETE /glossary/words/{user_word_id}`: remove a word from the user's glossary.
- `POST /glossary/words/{user_word_id}/notes`: add a personal note.

## Reviews

- `GET /reviews/due`: list words due for review.
- `POST /reviews/{user_word_id}/attempts`: record a review attempt.
- `GET /reviews/history`: list review history.

## Tags

- `GET /tags`: list user tags.
- `POST /tags`: create a tag.
- `PATCH /tags/{tag_id}`: update a tag.
- `DELETE /tags/{tag_id}`: delete a tag.
- `POST /glossary/words/{user_word_id}/tags/{tag_id}`: attach a tag.
- `DELETE /glossary/words/{user_word_id}/tags/{tag_id}`: detach a tag.
