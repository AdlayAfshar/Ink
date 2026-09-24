import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import "./App.css";
import { lookupDictionary } from "./api/dictionary";

function App() {
  const [word, setWord] = useState("");
  const [searchWord, setSearchWord] = useState("");

  const {
    data: result,
    error,
    isFetching,
  } = useQuery({
    queryKey: ["dictionary", searchWord],
    queryFn: () => lookupDictionary(searchWord),
    enabled: Boolean(searchWord),
    retry: false,
    staleTime: 5 * 60 * 1000,
  });

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedWord = word.trim();

    if (!trimmedWord) {
      return;
    }

    setSearchWord(trimmedWord);
  }

  return (
    <main>
      <h1>Ink Dictionary</h1>

      <form onSubmit={handleSubmit}>
        <input
          id="word-search"
          type="text"
          value={word}
          onChange={(event) => setWord(event.target.value)}
          placeholder="Enter a word"
        />

        <button type="submit" disabled={isFetching || !word.trim()}>
          {isFetching ? "Searching..." : "Search"}
        </button>
      </form>

      {error && <p>{error.message}</p>}

      {result && (
        <section>
          <h2>{result.word}</h2>

          {result.phonetic && <p>{result.phonetic}</p>}

          {result.audio_url && (
            <audio controls src={result.audio_url}>
              Your browser does not support audio playback.
            </audio>
          )}

          {result.definitions.map((definition, index) => (
            <article
              key={`${definition.part_of_speech ?? "unknown"}-${definition.definition}-${index}`}
            >
              {definition.part_of_speech && <p>{definition.part_of_speech}</p>}

              <p>{definition.definition}</p>

              {definition.example && (
                <p>
                  <strong>Example:</strong> {definition.example}
                </p>
              )}

              {definition.synonyms.length > 0 && (
                <p>
                  <strong>Synonyms:</strong> {definition.synonyms.join(", ")}
                </p>
              )}

              {definition.antonyms.length > 0 && (
                <p>
                  <strong>Antonyms:</strong> {definition.antonyms.join(", ")}
                </p>
              )}
            </article>
          ))}
        </section>
      )}
    </main>
  );
}

export default App;
