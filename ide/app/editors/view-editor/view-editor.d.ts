interface PlominoVocabularyViewData {
    results: { Type: string; id: string }[];
    total: number;
}

interface PlominoViewData {
    rows: Array<string>[];
    total: number;
    displayed: number;
}
