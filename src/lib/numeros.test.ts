import { describe, expect, it } from 'vitest';
import { formatoRango } from './numeros';

describe('formatoRango', () => {
  it('muestra repeticiones, segundos y minutos', () => {
    expect(formatoRango([6, 10], 'carga')).toBe('6–10');
    expect(formatoRango([5, 5], 'salto')).toBe('5');
    expect(formatoRango([20, 40], 'tiempo')).toBe('20–40 s');
    expect(formatoRango([900, 1500], 'tiempo')).toBe('15–25 min');
    expect(formatoRango([240, 240], 'tiempo')).toBe('4 min');
  });
});
