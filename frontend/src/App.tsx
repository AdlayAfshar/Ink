import { useState } from "react";
import "./App.css";

type DictionaryDefinition = {
  part_of_speech: string | null;
  definition: string;
  example: string | null;
  synonyms: string[];
  antonyms: string[];
};

type DictionaryEntry = {
  word: string;
  phonetic: string | null;
  audio_url: string | null;
  definitions: DictionaryDefinition[];
};

function App() {
  const [word, setWord] = useState("");
  const [result, setResult] = useState<DictionaryEntry | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const searchWord = word.trim();

    if (!searchWord) {
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;

      if (!apiBaseUrl) {
        throw new Error("VITE_API_BASE_URL is not configured");
      }

      const response = await fetch(
        `${apiBaseUrl}/dictionary/lookup/${encodeURIComponent(searchWord)}`,
      );

      if (response.status === 404) {
        throw new Error("Word not found");
      }

      if (response.status === 502) {
        throw new Error("Dictionary service is temporarily unavailable");
      }

      if (!response.ok) {
        throw new Error("Unable to search for this word");
      }

      const data: DictionaryEntry = await response.json();

      setResult(data);
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError("Something went wrong");
      }
    } finally {
      setLoading(false);
    }
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

        <button type="submit" disabled={loading || !word.trim()}>
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      {error && <p>{error}</p>}

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
