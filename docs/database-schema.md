# Database Schema

## Global Versus User-Specific Data

Global dictionary data is shared across all users and represents facts from dictionary providers. User-specific data belongs to one user and represents personal learning state.

Examples:

- Global: `words`, `word_definitions`, `word_examples`, `word_synonyms`
- User-specific: `user_words`, `user_word_notes`, `tags`, `reviews`, `review_attempts`

## Proposed Tables

### users

Application accounts.

- `id`
- `email`
- `hashed_password`
- `created_at`
- `updated_at`

### words

Shared dictionary word records.

- `id`
- `text`
- `language`
- `provider`
- `provider_lookup_key`
- `created_at`
- `updated_at`

### word_definitions

Definitions for a word.

- `id`
- `word_id`
- `part_of_speech`
- `definition`
- `source`
- `created_at`

### word_examples

Example sentences tied to a definition or word.

- `id`
- `word_id`
- `definition_id`
- `example_text`
- `source`

### word_synonyms

Synonyms for a word or definition.

- `id`
- `word_id`
- `definition_id`
- `synonym`

### user_words

A user's saved vocabulary item.

- `id`
- `user_id`
- `word_id`
- `learning_status`
- `saved_at`
- `last_reviewed_at`
- `next_review_at`

### user_word_notes

Personal notes for a saved word.

- `id`
- `user_word_id`
- `note`
- `created_at`
- `updated_at`

### tags

User-owned tags.

- `id`
- `user_id`
- `name`
- `created_at`

### user_word_tags

Join table between saved words and tags.

- `user_word_id`
- `tag_id`

### reviews

Review scheduling state for a saved word.

- `id`
- `user_word_id`
- `interval_days`
- `ease_factor`
- `due_at`
- `created_at`
- `updated_at`

### review_attempts

History of review attempts.

- `id`
- `review_id`
- `user_word_id`
- `result`
- `attempted_at`
- `response_time_ms`
