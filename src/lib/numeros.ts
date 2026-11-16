/** Acepta coma o punto decimal. Devuelve null si no hay numero. */
export function aNumero(texto: string): number | null {
  const limpio = texto.trim().replace(',', '.');
  if (limpio === '') return null;
  const n = Number.parseFloat(limpio);
  return Number.isFinite(n) ? n : null;
}

export function textoDe(valor: number | null | undefined): string {
  return valor === null || valor === undefined ? '' : String(valor);
}

/**
 * Rango de una prescripcion: "6–10" en repeticiones, "20–40 s" en tiempo y,
 * desde dos minutos, en minutos ("15–25 min") para que un trote se lea.
 */
export function formatoRango([min, max]: readonly [number, number], tipo: string): string {
  const texto = (a: number, b: number) => (a === b ? `${a}` : `${a}–${b}`);
  if (tipo !== 'tiempo') return texto(min, max);
  if (min >= 120) return `${texto(Math.round(min / 60), Math.round(max / 60))} min`;
  return `${texto(min, max)} s`;
}

export function fechaCorta(iso: string): string {
  const p = iso.split('-');
  return p.length === 3 ? `${p[2]}/${p[1]}` : iso;
}
