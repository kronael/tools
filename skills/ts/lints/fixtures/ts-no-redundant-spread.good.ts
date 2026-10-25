export {}
const a = [1, 2, 3]
const f = (n: number) => n > 1
const kept = a.filter(f)
const merged = [...a.filter(f), 99]
const chars = [..."text".slice(1)]
const values: number[] = [...new Uint8Array([1, 2]).map(n => n + 1)]
const filtered: number[] = [...new Uint8Array([1, 2]).filter(n => n > 1)]
const other = [...new Set([1, 2]).values().map(n => n + 1)]
