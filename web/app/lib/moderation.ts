// ml/generate/ng_words.txt と同期。運用開始前に要レビュー・拡充
export const NG_WORDS = ["死ね", "殺す", "バカ野郎"];

export function matchesFormat(
  title: string,
  suffix = "奴",
  minLen = 3,
  maxLen = 40
): boolean {
  if (!title.endsWith(suffix)) return false;
  if (title.length < minLen || title.length > maxLen) return false;
  if (/https?:\/\/\S+/.test(title)) return false;
  return true;
}

export function containsNgWord(text: string, ngWords: string[] = NG_WORDS): string | null {
  const normalized = text.normalize("NFKC").toLowerCase();
  for (const word of ngWords) {
    if (normalized.includes(word.normalize("NFKC").toLowerCase())) return word;
  }
  return null;
}

export function isAppropriate(text: string, ngWords: string[] = NG_WORDS): boolean {
  return containsNgWord(text, ngWords) === null;
}
