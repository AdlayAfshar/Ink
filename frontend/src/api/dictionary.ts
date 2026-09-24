export type DictionaryDefinition = {
  part_of_speech: string | null;
  definition: string;
  example: string | null;
  synonyms: string[];
  antonyms: string[];
};

export type DictionaryEntry = {
  word: string;
  phonetic: string | null;
  audio_url: string | null;
  definitions: DictionaryDefinition[];
};

export async function lookupDictionary(
  word: string,
): Promise<DictionaryEntry> {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;

  if (!apiBaseUrl) {
    throw new Error("VITE_API_BASE_URL is not configured");
  }

  const response = await fetch(
    `${apiBaseUrl}/dictionary/lookup/${encodeURIComponent(word)}`,
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

  return response.json() as Promise<DictionaryEntry>;
}
