interface PlominoTabUnit {
  id: string;
  url: string;
  editor: 'layout'|'code'|'view';
  label: string;
  isDirty?: boolean;
}
